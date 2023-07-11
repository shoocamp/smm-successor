import datetime
import logging
from pathlib import Path
from typing import List

from fastapi import UploadFile, File, Form, APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from typing_extensions import Annotated

from smm_successor.auth import get_password_hash, ACCESS_TOKEN_EXPIRE_DAYS, \
    create_access_token, authenticate_user, get_current_user
from smm_successor.config import CONFIG
from smm_successor.db import Storage
from smm_successor.models.user import UserInDB, BaseUser
from smm_successor.models.video import SocialPlatform, VideoStatus, Video, VideoInfo, VideoInDB, VideoEdit
from smm_successor.publishers import YoutubePublisher, VKPublisher

logger = logging.getLogger(__name__)

api_router = APIRouter()

storage = Storage(connection_uri=CONFIG["database"]["uri"])

PUBLISHERS = {
    SocialPlatform.vk: VKPublisher(CONFIG['vk']['token']),
    SocialPlatform.youtube: YoutubePublisher(CONFIG['youtube']['secret_file_path']),
}


@api_router.post("/api/v1/users/signup")
def sign_up(
        username: Annotated[str, Form(...)],
        password: Annotated[str, Form(...)],
        email: Annotated[str, Form(...)]
):
    hashed_password = get_password_hash(password)
    user = UserInDB(
        username=username,
        email=email,
        hashed_password=hashed_password
    )

    storage.create_new_user(user)
    return RedirectResponse(url='/api/v1/users/signin')


@api_router.post("/api/v1/users/signin")
def sign_in(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.get("/api/v1/users/info")
def user_info(current_user: Annotated[UserInDB, Depends(get_current_user)]) -> BaseUser:
    return current_user


@api_router.post("/api/v1/videos/")
def upload_video(
        current_user: Annotated[UserInDB, Depends(get_current_user)],
        title: str = Form(...),
        description: str = Form(...),
        youtube: bool = Form(False),
        vk: bool = Form(False),
        time_to_publish: datetime.datetime = Form(datetime.datetime.now()),
        file: UploadFile = File(...),
) -> VideoInDB:
    base_path = CONFIG['storage']['path']
    file_path = Path(base_path, file.filename)

    # ugly, think how to improve
    target_platforms = []
    if vk:
        target_platforms.append(SocialPlatform.vk)
    if youtube:
        target_platforms.append(SocialPlatform.youtube)

    incoming_video = Video(
        owner_id=current_user.id,
        info=VideoInfo(
            title=title,
            description=description,
        ),
        time_to_publish=time_to_publish,
        file_path=str(file_path),
        target_platforms=target_platforms,
        status=VideoStatus.WAITING,
        platform_status={},
    )

    # save a file locally
    with file_path.open("wb") as f:
        f.write(file.file.read())

    # save meta info in a database
    video_in_db = storage.add_video(incoming_video)

    # upload a file
    for platform in target_platforms:
        logger.info(f"Uploading video (id: {video_in_db.id}, user_id: {video_in_db.owner_id}) to {platform}")

        # set a video status
        storage.update_video(video_in_db.id, {"status": VideoStatus.UPLOADING})

        # upload
        platform_status = PUBLISHERS[platform].upload(video_in_db)

        # update platform specific status
        video_in_db.platform_status[platform] = platform_status
        storage.update_video(video_in_db.id, {"platform_status": video_in_db.platform_status})

        logger.info(f"Video (id: {video_in_db.id}, user_id: {video_in_db.owner_id}) uploaded to {platform} ")

    # set a video status
    storage.update_video(video_in_db.id, {"status": VideoStatus.UPLOADED})

    return video_in_db


@api_router.get("/api/v1/videos")
def get_videos(current_user: Annotated[UserInDB, Depends(get_current_user)]) -> List[VideoInDB]:
    return storage.get_videos_for_user(current_user.id)


@api_router.get("/api/v1/videos/{video_id}")
def get_videos(current_user: Annotated[UserInDB, Depends(get_current_user)], video_id) -> VideoInDB:
    video = storage.get_video_by_id(video_id)
    if video.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The user is not the owner of the video")
    return video


@api_router.put("/api/v1/videos/{video_id}")
def edit_video(
        current_user: Annotated[UserInDB, Depends(get_current_user)],
        video_id: str,
        new_video: VideoEdit,
) -> VideoInDB:
    video = storage.get_video_by_id(video_id)
    if video.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The user is not the owner of the video")

    if video.status is VideoStatus.UPLOADING:
        raise HTTPException(status.HTTP_423_LOCKED, detail="Video is not ready")

    new_values = {}

    if new_video.info.title:
        new_values['info.title'] = new_video.info.title

    if new_video.info.description:
        new_values['info.description'] = new_video.info.description

    if new_video.target_platforms:
        # TODO: trigger to upload/delete
        new_values['target_platforms'] = new_video.target_platforms

    if new_video.time_to_publish:
        new_values['time_to_publish'] = new_video.time_to_publish

    if len(new_values) == 0:
        # Return an original video if nothing changed
        return video

    updated_video = storage.update_video(video.id, updated_fields=new_values)

    if video.status == VideoStatus.UPLOADED:
        # update info
        for platform in video.target_platforms:
            # TODO: check if a video was already uploaded
            PUBLISHERS[platform].edit_video(updated_video)

    return updated_video


@api_router.put("/api/v1/videos/delete/{video_id}")
def delete_video(
        current_user: Annotated[UserInDB, Depends(get_current_user)],
        video_id: str,
        youtube: bool = Form(False),
        vk: bool = Form(False)
):

    target_platforms = []
    if vk:
        target_platforms.append(SocialPlatform.vk)
    if youtube:
        target_platforms.append(SocialPlatform.youtube)

    video_in_db = storage.get_video_by_id(video_id)

    if video_in_db.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The user is not the owner of the video")

    if video_in_db.status is VideoStatus.UPLOADING:
        raise HTTPException(status.HTTP_423_LOCKED, detail="Video is not ready")

    for platform in target_platforms:
        logger.info(f"Deleting video (id: {video_in_db.id}, user_id: {video_in_db.owner_id}) from {platform}")

        # deleting
        platform_status = PUBLISHERS[platform].delete_video(video_in_db)

        video_in_db.platform_status[platform] = platform_status
        storage.update_video(video_in_db.id, {"platform_status": video_in_db.platform_status})

        logger.info(f"Video (id: {video_in_db.id}, user_id: {video_in_db.owner_id}) deleted from {platform} ")

    # # set a video status
    # storage.update_video(videoid, {"status": VideoStatus.UPLOADED})

    return video_in_db

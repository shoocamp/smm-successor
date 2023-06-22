import datetime
import hashlib
import secrets

import toml
from fastapi import UploadFile, File, Form, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated

from smm_successor.db import Storage
from smm_successor.models import VideoInfo, TargetPlatform, APIResponse
from smm_successor.publishers import YoutubePublisher, VKPublisher

api_router = APIRouter()

conf = toml.load("config.toml")

storage = Storage(uri=conf["database"]["uri"])
youtube_publisher = YoutubePublisher(conf['youtube']['secret_file_path'])
vk_publisher = VKPublisher(conf['vk']['token'])

security = HTTPBasic()


def get_current_user_id(
        credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    current_username = credentials.username
    current_password = credentials.password
    password_hash = hashlib.md5(current_password.encode()).hexdigest()
    password_from_db = storage.get_md5_pass_by_name(current_username)
    is_correct_password = secrets.compare_digest(
        password_hash, password_from_db
    )
    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect name or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    user_name = credentials.username
    user_id = storage.get_user_id_by_name(user_name)
    return user_id


@api_router.post("/api/v1/signup")
def sign_up(name, password):
    password_hash = hashlib.md5(password.encode()).hexdigest()
    user_id = storage.create_new_user(name=name, password=password_hash)
    return user_id


@api_router.post("/api/v1/upload_video")
def upload_video(user_id: Annotated[str, Depends(get_current_user_id)],
                 title=Form(...),
                 description=Form(...),
                 target_platform: TargetPlatform = Form(...),
                 time_to_publish: datetime.datetime = Form(datetime.datetime.now()),
                 file: UploadFile = File(...)) -> APIResponse:
    info = VideoInfo(title=title,
                     description=description,
                     target_platform=target_platform,
                     time_to_publish=time_to_publish)

    file_path = file.filename

    with open(file.filename, "wb") as f:
        f.write(file.file.read())

    path = storage.add_video_meta_info(user_id=user_id, info=dict(info), path=file_path)

    if info.target_platform == TargetPlatform.all:
        vk_response = vk_publisher.upload(file_path, title=info.title, description=info.description)
        youtube_response = youtube_publisher.upload(file_path, title=info.title, description=info.description)
        result = {"vk": vk_response, "youtube": youtube_response, "path": path}
    elif info.target_platform == TargetPlatform.vk:
        vk_response = vk_publisher.upload(file_path, title=info.title, description=info.description)
        result = {"vk": vk_response, "path": path}
    elif info.target_platform == TargetPlatform.youtube:
        youtube_response = youtube_publisher.upload(file_path, title=info.title, description=info.description)
        result = {"youtube": youtube_response, "path": path}
    else:
        raise HTTPException(402, f"Unsupported platform: '{info.target_platform}'")

    return APIResponse(result=result)

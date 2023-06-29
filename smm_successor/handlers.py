import datetime
import hashlib
import secrets

import toml
from fastapi import UploadFile, File, Form, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing_extensions import Annotated
from typing import Optional

from smm_successor.db import Storage
from smm_successor.models import VideoStatus, VideoInfo, TargetPlatforms, APIResponse, SignUp, User, LogIn, VideoFile
from smm_successor.publishers import YoutubePublisher, VKPublisher

api_router = APIRouter()

conf = toml.load("smm_successor/config.toml")

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
def sign_up(data: SignUp) -> APIResponse:
    password_hash = hashlib.md5(data.password.encode()).hexdigest()
    user_id = storage.create_new_user(name=data.username, password=password_hash)
    return APIResponse(result=User(user_id, data.username))


@api_router.post("/api/v1/login")
def sign_in(data: LogIn) -> APIResponse:
    password_hash = hashlib.md5(data.password.encode()).hexdigest()
    user_id = storage.get_user_id_by_name(name=data.username)
    # TODO: check password, exchange to a token
    return APIResponse(result=User(user_id, data.username))


@api_router.post("/api/v1/upload_video")
def upload_video(user_id: Annotated[str, Depends(get_current_user_id)],
                 title=Form(...),
                 description=Form(...),
                 target_platforms: TargetPlatforms = Form(...),
                 time_to_publish: datetime.datetime = Form(datetime.datetime.now()),
                 file: UploadFile = File(...)) -> APIResponse:
    file_data = VideoFile(
        info=VideoInfo(title=title,
                       description=description,
                       time_to_publish=time_to_publish),
        file_path=file.filename,
        target_platforms=[target_platforms],
        status='waiting'
    )

    file_data_dict = {
        'info': file_data.info.dict(),
        'file_path': str(file_data.file_path),
        'target_platforms': [tp.value for tp in file_data.target_platforms],
        'status': file_data.status
    }
    with open(file.filename, "wb") as f:
        f.write(file.file.read())

    file_path = file.filename

    file_db = storage.add_file_data_to_db(user_id=user_id, file_data=file_data_dict)

    record_filter = {'_id': file_db['_id']}

    if file_data.target_platforms == [TargetPlatforms.all]:
        vk_response = vk_publisher.upload(file_path, title=file_data.info.title,
                                          description=file_data.info.description)
        youtube_response = youtube_publisher.upload(file_path, title=file_data.info.title,
                                                    description=file_data.info.description)
        result = {"vk": vk_response, "youtube": youtube_response, "db": file_db}

        storage.update_file_data(record_filter, {'file_data.status': VideoStatus.UPLOADED})
        storage.update_file_data(record_filter, {'vk': vk_response, 'youtube': youtube_response})

    elif file_data.target_platforms == [TargetPlatforms.vk]:
        vk_response = vk_publisher.upload(file_path, title=file_data.info.title,
                                          description=file_data.info.description)
        result = {"vk": vk_response, "db": file_db}

        storage.update_file_data(record_filter, {'file_data.status': VideoStatus.UPLOADED})
        storage.update_file_data(record_filter, {'vk': vk_response})

    elif file_data.target_platforms == [TargetPlatforms.youtube]:
        youtube_response = youtube_publisher.upload(file_path, title=file_data.info.title,
                                                    description=file_data.info.description)
        result = {"youtube": youtube_response, "db": file_db}

        storage.update_file_data(record_filter, {'status': VideoStatus.UPLOADED})
        storage.update_file_data(record_filter, {'youtube': youtube_response})

    else:
        raise HTTPException(402, f"Unsupported platform: '{file_data.target_platforms}'")

    return APIResponse(result=result)


@api_router.get("/api/v1/get_list_with_status")
def get_list(user_id: Annotated[str, Depends(get_current_user_id)],
             status: VideoStatus):
    result = storage.get_list_of_video(user_id, status)
    return result


@api_router.put("/api/v1/edit_file_information")
def edit_file(user_id: Annotated[str, Depends(get_current_user_id)], db_id: int,
              title: Optional[str] = None,
              description: Optional[str] = None,
              target_platforms: Optional[TargetPlatforms] = Form(None),
              time_to_publish: datetime.datetime = Form(datetime.datetime.now()),
              ):

    file_data = storage.build_file_data_from_db(db_id)
    # TODO: add logic for different quantity of parameters changing
    #  (may be one by one?...or leve previous one if no new)
    if file_data.status == VideoStatus.WAITING:
        record_filter = {'_id': db_id}
        new_value = {'file_data.info.title': title,
                     'file_data.info.description': description,
                     'file_data.target_platforms': target_platforms,
                     'file_data.info.time_to_publish': time_to_publish}

        storage.update_file_data(record_filter=record_filter, new_value=new_value)

    # TODO: taking video_id from request.
    #  finish code

    elif file_data.status == VideoStatus.UPLOADED:
        if file_data.target_platforms == [TargetPlatforms.vk]:
            response = vk_publisher.edit_data(video_id=456239089, new_title=title, new_description=description)

    return response

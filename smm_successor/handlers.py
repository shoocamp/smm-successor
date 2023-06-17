import datetime

import toml
from fastapi import UploadFile, File, Form, APIRouter, HTTPException

from db import Storage
from models import VideoInfo, TargetPlatform, APIResponse
from publishers import YoutubePublisher, VKPublisher

api_router = APIRouter()

conf = toml.load("config.toml")

storage = Storage(uri=conf["database"]["uri"])
youtube_publisher = YoutubePublisher(conf['youtube']['secret_file_path'])
vk_publisher = VKPublisher(conf['vk']['token'])

user_id = 2


@api_router.post("/api/v1/upload_video")
def upload_video(title=Form(...),
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

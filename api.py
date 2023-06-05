from fastapi import UploadFile, File, Form, APIRouter
from models import VideoInfo, TargetPlatform
import toml
from db import Storage
from youtube import upload

api_router = APIRouter()

conf = toml.load("/Users/sergeyzaitsev/PycharmProjects/smm-successor/db_config.toml")
storage = Storage(uri=conf["database"]["uri"])
user_id = 1

@api_router.post("/api/v1/upload_video")
def upload_video(title=Form(...),
                 description=Form(...),
                 target_platform: TargetPlatform = Form(...),
                 time_to_publish=Form(...),
                 file: UploadFile = File(...)):

    info = VideoInfo(title=title,
                     description=description,
                     target_platform=target_platform,
                     time_to_publish=time_to_publish)

    file_path = "/Users/sergeyzaitsev/PycharmProjects/smm-successor/" + file.filename

    with open(file.filename, "wb") as f:
        f.write(file.file.read())

    x = storage.add_info_and_path(user_id=user_id, info=dict(info), path=file_path)

    you = upload(file_path)

    return x, you


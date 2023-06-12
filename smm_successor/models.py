from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel


class TargetPlatform(str, Enum):
    youtube = "YOUTUBE"
    vk = "VK"
    all = "ALL PLATFORMS"


class VideoInfo(BaseModel):
    title: str
    description: str
    target_platform: str
    time_to_publish: datetime


class VideoStatus(str, Enum):
    WAITING = "waiting"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    ERROR = "error"


class VideoFile(BaseModel):
    db_id: str
    info: VideoInfo
    file_path: Path
    status: VideoStatus


class ApiResponseStatus(Enum):
    OK = "ok"
    ERROR = "error"


class APIResponse(BaseModel):
    status: ApiResponseStatus = ApiResponseStatus.OK
    result: dict

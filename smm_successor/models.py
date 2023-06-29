from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class User:
    def __init__(self, db_id, username):
        self.db_id = db_id
        self.username = username

    def __repr__(self):
        return f"User({self.db_id}, {self.username}"


class SignUp(BaseModel):
    username: str
    password: str
    email: str


class LogIn(BaseModel):
    password: str
    username: str


class TargetPlatforms(str, Enum):
    youtube = "YOUTUBE"
    vk = "VK"
    all = "ALL PLATFORMS"


class VideoInfo(BaseModel):
    title: str
    description: str
    time_to_publish: datetime


class VideoStatus(str, Enum):
    WAITING = "waiting"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    ERROR = "error"


class VideoFile(BaseModel):
    info: VideoInfo
    file_path: Path
    target_platforms: list[TargetPlatforms]
    status: VideoStatus


class ApiResponseStatus(Enum):
    OK = "ok"
    ERROR = "error"


class APIResponse(BaseModel):
    status: ApiResponseStatus = ApiResponseStatus.OK
    result: Any

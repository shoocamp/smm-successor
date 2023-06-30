from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Union

from pydantic import BaseModel, Field


class SocialPlatform(str, Enum):
    youtube = "YOUTUBE"
    vk = "VK"


class VKVideoInfo(BaseModel):
    video_hash: str
    size: int
    direct_link: str
    owner_id: int
    video_id: int


class VideoInfo(BaseModel):
    title: str = Field(default=None, title="Video title")
    description: str = Field(default=None, title="Video description")


class VideoStatus(str, Enum):
    WAITING = "waiting"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    ERROR = "error"


class VideoEdit(BaseModel):
    info: Optional[VideoInfo]
    time_to_publish: Optional[datetime]
    target_platforms: Optional[List[SocialPlatform]]


class Video(VideoEdit):
    owner_id: str
    file_path: Optional[str]
    status: VideoStatus
    platform_status: Dict[SocialPlatform, Union[VKVideoInfo, dict]]


class VideoInDB(Video):
    id: str

    @classmethod
    def from_db(cls, data: Dict) -> 'VideoInDB':
        _id = str(data['_id'])
        del data['_id']

        return cls(
            id=_id,
            **data
        )

from enum import Enum

from pydantic import BaseModel


class TargetPlatform(str, Enum):
    youtube = "youtube"
    vk = "vk"
    both = "both"


class VideoInfo(BaseModel):
    title: str
    description: str
    target_platform: TargetPlatform = str
    time_to_publish: str


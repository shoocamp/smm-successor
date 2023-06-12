from enum import Enum

from pydantic import BaseModel


class TargetPlatform(str, Enum):
    youtube = "YOUTUBE"
    vk = "VK"
    both = "ALL PLATFORMS"


class VideoInfo(BaseModel):
    title: str
    description: str
    target_platform: str
    time_to_publish: str


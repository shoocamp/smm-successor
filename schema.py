from pydantic import BaseModel


class Video_info(BaseModel):
    title: str
    description: str
    target_platform: str
    time_to_publish: str


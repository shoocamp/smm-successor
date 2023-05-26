from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

app = FastAPI()


class Video(BaseModel):
    title: str
    description: str
    target_platform: str
    time_to_publish: str


@app.post("/videos")
async def upload_video(video: Video, file: UploadFile = File(...)):
    # Process the video data and file here
    # You can access the video fields using `video.title`, `video.description`, etc.
    # You can access the uploaded file using `file.filename` and `file.file` properties
    # Perform necessary operations like saving the file, storing metadata, etc.

    # Example response
    return {"message": "Video uploaded successfully"}

from fastapi import UploadFile, File, Form, APIRouter

from schema import Video_info

video_router = APIRouter()


@video_router.post("/api/v1/upload_video")
async def upload_video(title=Form(...),
                       description=Form(...),
                       target_platform=Form(...),
                       time_to_publish=Form(...),
                       file: UploadFile = File(...)):

    info = Video_info(title=title,
                      description=description,
                      target_platform=target_platform,
                      time_to_publish=time_to_publish)

    contents = await file.read()
    with open(file.filename, "wb") as f:
        f.write(contents)
    return {"filename": file.filename, "info": info}


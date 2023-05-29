from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel


class Video_info(BaseModel):
    title: str
    description: str
    target_platform: str
    time_to_publish: str


app = FastAPI()

@app.post("/api/v1/upload_video")
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
    # Сохранение файла на сервере
    with open(file.filename, "wb") as f:
        f.write(contents)
    # return video
    return {"filename": file.filename, "info": info}
    # Example response
    # return {"message": "Video uploaded successfully"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="http://127.0.0.1", port=8000)

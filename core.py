from models import VideoInfo


class VideoFile:
    VALID_STATUSES = ["waiting", "uploading", "uploaded"]

    def __init__(self, db_id, info: VideoInfo, file_path, status):
        self.db_id = db_id,
        self.info = info,
        self.file_path = file_path
        self.status = status


class Publisher:
    def __init__(self, video_file: VideoFile):
        self.video_file = video_file


    def place_video(self):
        ...

    def delete_video(self):
        ...

    def edit_video_data(self):
        ...


class Youtube(Publisher):

    def place_video(self):
        ...

    def delete_video(self):
        ...

    def edit_video_data(self):
        ...


class Vk(Publisher):
    ...

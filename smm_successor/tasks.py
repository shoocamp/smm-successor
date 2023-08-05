import logging

from celery import Celery

from smm_successor.config import CONFIG
from smm_successor.db import Storage
from smm_successor.models.video import VideoInDB, SocialPlatform
from smm_successor.publishers import VKPublisher, YoutubePublisher

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery('tasks', broker_url='redis://localhost:6379/0', result_backend='redis://localhost:6379/0', concurrency=2)

storage = Storage(connection_uri=CONFIG["database"]["uri"])

PUBLISHERS = {
    SocialPlatform.vk: VKPublisher(CONFIG['vk']['token']),
    SocialPlatform.youtube: YoutubePublisher(CONFIG['youtube']['secret_file_path']),
}


@app.task
def upload_video_worker(platform: SocialPlatform, video_in_db: dict):
    publisher = PUBLISHERS[platform]
    video = VideoInDB(**video_in_db)

    logger.info(f"Run task 'upload video'. Video id: {video.id}', platform: {platform}")
    result = publisher.upload(video)
    video.platform_status[platform] = result
    storage.update_video(video.id, {"platform_status": video.platform_status})
    logger.info(f"Task 'upload video is done. Video id: {video.id}', platform: {platform}")
    return result

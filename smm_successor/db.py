from typing import List, Dict, Any, Optional

from bson import ObjectId
from pymongo.mongo_client import MongoClient

from smm_successor.models.user import BaseUser, UserInDB
from smm_successor.models.video import Video, VideoInDB


class Storage:
    def __init__(self, connection_uri):
        client = MongoClient(connection_uri)
        db = client['smm']
        self.users_collection = db["users"]
        self.content_collection = db["content"]

    def add_video(self, video: Video) -> VideoInDB:
        result = self.content_collection.insert_one(video.dict())
        raw_video = self.content_collection.find_one({'_id': ObjectId(result.inserted_id)})
        return VideoInDB.from_db(raw_video)

    def update_video(self, video_id: str, updated_fields: Dict[str, Any]) -> VideoInDB:
        self.content_collection.update_one({"_id": ObjectId(video_id)}, {"$set": updated_fields}, upsert=False)
        raw_video = self.content_collection.find_one({'_id': ObjectId(video_id)})
        return VideoInDB.from_db(raw_video)

    def create_new_user(self, user: UserInDB) -> BaseUser:
        result = self.users_collection.insert_one({
            'username': user.username,
            'email': user.email,
            'hashed_password': user.hashed_password
        })

        raw_user: dict = self.users_collection.find_one({'_id': ObjectId(result.inserted_id)})

        if raw_user is None:
            raise RuntimeError("Unable to create a user")

        return BaseUser.from_db(raw_user)

    def get_user_by_name(self, username: str) -> BaseUser:
        raw_user = self.users_collection.find_one({'username': username})
        return BaseUser.from_db(raw_user)

    def get_user_hashed_password(self, username: str) -> Optional[str]:
        raw_user = self.users_collection.find_one({'username': username})
        if raw_user is None:
            return None
        return raw_user['hashed_password']

    def get_videos_for_user(self, user_id: str) -> List[VideoInDB]:
        result = self.content_collection.find({"owner_id": user_id})
        videos = []
        for raw_video in result:
            videos.append(VideoInDB.from_db(raw_video))
        return videos

    def get_video_by_id(self, video_id: str) -> VideoInDB:
        raw_video = self.content_collection.find_one({"_id": ObjectId(video_id)})
        return VideoInDB.from_db(raw_video)

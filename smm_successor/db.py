from pymongo.mongo_client import MongoClient
from pydantic import BaseModel
from smm_successor.models import VideoStatus, VideoInfo, TargetPlatforms, VideoFile


class Storage:
    def __init__(self, uri):
        self.uri = uri
        self.client = MongoClient(self.uri)

    def add_file_data_to_db(self, user_id, file_data: dict):
        def get_next_id():
            counter_meta_collection = db.counter
            counter = counter_meta_collection.find_one_and_update(
                {"_id": "users_content"},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=True
            )
            return counter["seq"]

        db = self.client["smm"]
        # db["users_content"].drop()  # do not forget to kill
        coll = db["users_content"]
        coll.insert_one({'_id': get_next_id(), 'user_id': user_id, 'file_data': dict(file_data)})
        return coll.find_one({'file_data': file_data})

    def update_file_data(self, record_filter, new_value):
        db = self.client["smm"]
        coll = db["users_content"]
        coll.update_one(record_filter, {"$set": new_value})
        return coll.find_one(record_filter)['file_data']['status']

    def create_new_user(self, name, password):
        db = self.client["smm"]
        coll = db["users"]

        def get_next_id():
            # Создание коллекции для хранения счетчика
            counter_collection = db.counter
            counter = counter_collection.find_one_and_update(
                {"_id": "users"},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=True
            )
            return counter["seq"]

        coll.insert_one({'_id': get_next_id(), 'name': name, 'password': password})
        last_document = coll.find().sort("_id", -1).limit(1)[0]

        return last_document["_id"]

    def get_md5_pass_by_name(self, name):
        db = self.client["smm"]
        coll = db["users"]
        result = coll.find_one({"name": name})
        return result["password"]

    def get_user_id_by_name(self, name):
        db = self.client["smm"]
        coll = db["users"]
        result = coll.find_one({"name": name})
        return result["_id"]

    def get_list_of_video(self, user_id, status):
        db = self.client["smm"]
        coll = db["users_content"]
        result = coll.find({'$and': [
            {"user_id": user_id},
            {"file_data.status": status}]})
        records = []
        for document in result:
            records.append(document)
        return records

    def build_file_data_from_db(self, db_id) -> VideoFile:
        db = self.client["smm"]
        coll = db["users_content"]
        result = coll.find_one({"_id": db_id})
        file_data = VideoFile(info=result['file_data']['info'],
                              file_path=result['file_data']['file_path'],
                              target_platforms=result['file_data']['target_platforms'],
                              status=result['file_data']['status'])
        return file_data

from pymongo.mongo_client import MongoClient

class Storage:
    def __init__(self, uri):
        self.uri = uri
        self.client = MongoClient(self.uri)

    def add_video_meta_info(self, user_id, info, path):
        db = self.client["smm"]
        db["users_content"].drop()  # do not forget to kill
        coll = db["users_content"]
        coll.insert_one({'_id': 1, 'user_id': user_id, 'info': info, 'path': path})
        return coll.find_one({'path': path})

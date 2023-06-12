from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi


class Storage:
    def __init__(self, uri):
        self.uri = uri
        self.client = MongoClient(self.uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

    def add_info_and_path(self, user_id, info, path):
        db = self.client["smm"]
        db["users_content"].drop() # do not forget to kill
        coll = db["users_content"]
        coll.insert_one({'_id': 1, 'user_id': user_id, 'info': info, 'path': path})
        return coll.find_one({'path': path})


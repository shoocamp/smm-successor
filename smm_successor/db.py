from pymongo.mongo_client import MongoClient


class Storage:
    def __init__(self, uri):
        self.uri = uri
        self.client = MongoClient(self.uri)

    def add_video_meta_info(self, user_id, info, path):
        def get_next_id():
            # Создание коллекции для хранения счетчика
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
        coll.insert_one({'_id': get_next_id(), 'user_id': user_id, 'info': info, 'path': path})
        return coll.find_one({'path': path})

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
        print(result)
        return result["password"]

    def get_user_id_by_name(self, name):
        db = self.client["smm"]
        coll = db["users"]
        result = coll.find_one({"name": name})
        print(result)
        return result["_id"]



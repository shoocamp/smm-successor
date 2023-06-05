class User:
    def __init__(self, db_id, username, media_file):
        self.db_id = db_id
        self.username = username
        self.media_file = media_file

        # self.default_list_id = default_list_id
    #
    # def __repr__(self):
    #     return f"User({self.db_id}, {self.username}, {self.default_list_id}"
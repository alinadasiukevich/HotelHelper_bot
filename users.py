import datetime


class Users:
    users = dict()

    def __init__(self, user_id):
        self.user_id = user_id
        self.city = None
        self.check_in = None
        self.check_out = None
        self.command = None
        self.time_of_use = None
        self.hotel_count = None
        self.need_photo = None
        self.num_photo = None
        self.hotels_res = []
        self.price_min = None
        self.price_max = None
        self.distance_min = None
        self.distance_max = None
        Users.add_user(user_id, self)

    @staticmethod
    def get_user(user_id):
        if Users.users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.users[user_id] = user

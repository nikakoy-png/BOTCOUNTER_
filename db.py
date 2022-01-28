from settings import *
import json
import random

class DB:

    def __init__(self, host, database):
        self.db_client = pymongo.MongoClient(host)
        self.current_db = self.db_client[f'{database}']
        self.collection_user = self.current_db['User']
        self.collection_admin = self.current_db['Admin']
        self.collection_seeker = self.current_db['Seeker']

    def create_new_seeker(self, telegram_id, telegram_id_found_user):
        request = {
            'telegram_id': telegram_id,
            'found_user': telegram_id_found_user,
            'status': 'active'
        }
        self.collection_seeker.insert_one(request)
        print(f"Pair found: {telegram_id} and {telegram_id_found_user}")

    def off_active_seek(self, telegram_id):
        self.collection_seeker.update_many({'telegram_id': telegram_id}, {"$set": {'status': 'off'}})

    def like_active_seek(self, telegram_id):
        self.collection_seeker.update_many({'telegram_id': telegram_id}, {"$set": {'status': 'like'}})

    def ok_active_seek(self, telegram_id, found_user):
        self.collection_seeker.update_one({'telegram_id': telegram_id, 'found_user': found_user}, {"$set": {'status': 'ok'}})

    def get_active_seek(self, telegram_id):
        return self.collection_seeker.find_one({'telegram_id': telegram_id, 'status': 'active'})['found_user']

    def drop_pair(self, telegram_id):
        self.collection_seeker.delete_one({'telegram_id': telegram_id})

    def get_list_pair_user(self, sex, interesting) -> list:
        list_of_id = []
        for x in self.collection_user.find({'sex': sex, 'interesting': interesting}):
            list_of_id.append(x['id'])
        return list_of_id

    def filter_of_twin(self, list_found_user, seeker_id):
        list_id_before_found = []
        for x in self.collection_seeker.find({'telegram_id': seeker_id}):
            list_id_before_found.append(x['found_user'])
        for x in list_id_before_found:
            if x in list_found_user:
                del list_found_user[list_found_user.index(x)]
        return list_found_user

    def get_user_with_city(self, list_found_user, city):
        list_user_with_city = []
        for x in list_found_user:
            if self.get_user(x)['city'] == city:
                list_user_with_city.append(x)
        if not list_user_with_city:
            return list_found_user
        return list_user_with_city

    def get_pair(self, telegram_id_seeker):
        try:
            seeker = self.get_user(telegram_id_seeker)
            city = seeker['city']
            bool_sex = False
            bool_interesting = False
            if seeker['interesting'] == 'Девушки':
                bool_sex = True
            if seeker['sex'] == 'Парень':
                bool_interesting = True
            found_sex = ('Парень', 'Девушка')[bool_sex]
            found_interesting = ('Девушки', 'Парни')[bool_interesting]
            list_found_user = self.get_user_with_city(
                self.filter_of_twin(
                    self.get_list_pair_user(
                        found_sex, found_interesting
                    ), telegram_id_seeker
                ), city
            )
            pair = random.choice(list_found_user)
            self.create_new_seeker(telegram_id_seeker, pair)
            return pair
        except Exception:
            return False

    def register_new_user(self, telegram_id, username):
        request = {
            'id': telegram_id,
            'login': username,
            'description': '',
            'like': 0,
            'views': 0,
            'city': None,
            'photo': None,
            'mutual': 0,
            'sex': "",
            'age': 0,
            'interesting': None,
            'name': "",
            'status': None
        }
        self.collection_user.insert_one(request)
        print(f"successful recorded {telegram_id}")

    def increment_row(self, telegram_id, row):
        value = self.get_user(telegram_id)[f'{row}']
        value = value + 1
        self.collection_user.update_one({'id': telegram_id}, {"$set": {f"{row}": value}})

    def set_value(self, telegram_id, row, value):
        self.collection_user.update_one({'id': telegram_id}, {"$set": {f"{row}": value}})

    def get_user(self, telegram_id):
        return self.collection_user.find_one({'id': telegram_id})

    def get_all_user(self):
        list_id_user = []
        for x in self.collection_user.find({}):
            list_id_user.append(x['id'])
        return list_id_user

    def get_id_admin(self):
        return self.collection_user.find_one({'status': 'Admin'})['id']

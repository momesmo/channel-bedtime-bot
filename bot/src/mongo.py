"""
This module contains the Mongo class.
"""
import pymongo
from customexceptions import MongoError


class Mongo:
    """
    This class represents the Mongo client.
    """
    def __init__(self, host="localhost", port=27017, db="bedtime_bot"):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[db]
        # self.collection = self.db[collection]

    def get_collection(self, collection):
        return self.db[collection]
    
    def get_guild_data(self, guild_id):
        return self.get_collection('guilds').find_one({'guild_id': guild_id})
    
    def update_guild_data(self, guild_id, data):
        return self.get_collection('guilds').update_one({'guild_id': guild_id}, {'$set': data}, upsert=True)
    
    def delete_guild_data(self, guild_id):
        return self.get_collection('guilds').delete_one({'guild_id': guild_id})

#     def get_db(self):
#         return self.db

#     def get_collection(self):
#         return self.collection

#     def get_guild(self, guild_id):
#         return self.collection.find_one({'guild_id': guild_id})

#     def create_guild(self, guild_id, channel_id):
#         try:
#             self.collection.insert_one({'guild_id': guild_id, 'channel_id': channel_id})
#         except pymongo.errors.DuplicateKeyError as e:
#             raise MongoError("Guild already exists.") from e
#         except Exception as e:
#             raise MongoError(e) from e

#     def create_or_update_guild(self, guild_id, properties):
#         return self.collection.update_one({'guild_id': guild_id}, {'$set': properties}, upsert=True)

#     def delete_guild(self, guild_id):
#         return self.collection.delete_one({'guild_id': guild_id})

# # TODO: implement validations for each operation

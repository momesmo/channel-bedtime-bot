"""
This module contains the Mongo class.
"""
from pymongo import MongoClient as PyMongoClient
# TODO: figure out why this doesn't work for pytest
# from customexceptions import MongoError
from datetime import datetime

class MongoClient:
    """
    This class represents the Mongo client.
    """
    def __init__(self, host="localhost", port=27017, username="user", password="password", db="discord_bot", timeout=10000):
        self.client = PyMongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            authSource=db,
            authMechanism="SCRAM-SHA-256",
            serverSelectionTimeoutMS=timeout
        )
        self.db = self.client[db]
        # self.collection = self.db[collection]

    # TODO: all methods are WIP

    def get_collection(self, collection):
        return self.db[collection]
    
    def get_guild(self, guild_id):
        return self.get_collection('guilds').find_one({'guild_id': guild_id}) or {}
    
    def update_guild(self, guild_id, data):
        guild_data = self.get_guild(guild_id)
        data['created_at'] = guild_data.get('created_at', datetime.now())
        data['updated_at'] = datetime.now()
        self.get_collection('guilds').update_one({'guild_id': guild_id}, {'$set': data}, upsert=True)

        # Get the _id of the updated/inserted document
        updated_doc = self.get_collection('guilds').find_one({'guild_id': guild_id})
        return updated_doc['_id']
    
    def delete_guild(self, guild_id):
        return self.get_collection('guilds').delete_one({'guild_id': guild_id})
    
    def get_guild_settings(self, guild_id=None, settings_id=None):
        if guild_id is not None:
            settings_id = self.get_guild(guild_id).get('guild_settings_id', None)
        if settings_id is None:
            return {}
        return self.get_collection('guild_settings').find_one({'_id': settings_id}) or {}
    
    def update_guild_settings(self, guild_id, data):
        # TODO: different fields if document is new or updated
        guild_settings_data = self.get_guild_settings(guild_id=guild_id)
        data['created_at'] = guild_settings_data.get('created_at', datetime.now())
        data['updated_at'] = datetime.now()
        result = self.get_collection('guild_settings').update_one({'guild_id': guild_id}, {'$set': data}, upsert=True)
        
        # Get the _id of the updated/inserted document
        updated_doc = self.get_collection('guild_settings').find_one({'guild_id': guild_id})
        return updated_doc['_id']

    def delete_guild_settings(self, guild_id=None, settings_id=None):
        if guild_id is not None:
            return self.get_collection('guild_settings').delete_one({'guild_id': guild_id})
        if settings_id is not None:
            return self.get_collection('guild_settings').delete_one({'_id': settings_id})
        
    ### PURGE METHODS ###
    def purge_all(self):
        self.get_collection('guilds').delete_many({})
        self.get_collection('guild_settings').delete_many({})

# TODO: implement validations for each operation

if __name__ == "__main__":
    mongo_client = MongoClient(username="user", password="password")
    # print(mongo_client.get_guild_data(1234567890))
    pass

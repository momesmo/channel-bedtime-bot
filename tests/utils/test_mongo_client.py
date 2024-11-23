# TODO: develop tests with https://testcontainers.com/modules/mongodb/
# TODO: add tests for mongo_client
import os
import re
import pytest
from testcontainers.mongodb import MongoDbContainer
from helpers.mongo_client import MongoClient

mongo_container = MongoDbContainer("mongo:latest")

@pytest.fixture(scope="module", autouse=True)
def setup(request):
    mongo_container.start()

    def remove_container():
        mongo_container.stop()
    request.addfinalizer(remove_container)

    print("Waiting for MongoDB to start...")
    mongo_container._connect()
    connection_url = mongo_container.get_connection_url()
    url_components = re.search(r"mongodb://(.*):(.*)@(.*):(.*)", connection_url)
    pytest.mongo_host = url_components.group(3)
    pytest.mongo_port = int(url_components.group(4))
    pytest.mongo_username = url_components.group(1)
    pytest.mongo_password = url_components.group(2)
    pytest.mongo_auth_source = "admin"

@pytest.fixture(scope="function", autouse=True)
def setup_data():
    mongo_client = MongoClient(host=pytest.mongo_host, port=pytest.mongo_port, username=pytest.mongo_username, password=pytest.mongo_password, auth_source=pytest.mongo_auth_source)
    mongo_client.purge_all()

def test_mongo_client():
    mongo_client = MongoClient(host=pytest.mongo_host, port=pytest.mongo_port, username=pytest.mongo_username, password=pytest.mongo_password, auth_source=pytest.mongo_auth_source)
    collection = mongo_client.get_collection('guilds')
    assert collection.count_documents({}) == 0

class TestGuild:
    # TODO: add tests for update_guild
    # TODO: add tests for get_guild
    # TODO: add tests for get_collection
    # TODO: add tests for get_db
    # TODO: add tests for update_guild
    # TODO: add tests for delete_guild
    # TODO: add tests for get_guild_settings
    # TODO: add tests for update_guild_settings 
    # TODO: add tests for delete_guild_settings
    def test_update(self):
        mongo_client = MongoClient(host=pytest.mongo_host, port=pytest.mongo_port, username=pytest.mongo_username, password=pytest.mongo_password, auth_source=pytest.mongo_auth_source)
        guild_id = mongo_client.update_guild(guild_id=1234567890, data={'name': 'Test Guild'})
        guild = mongo_client.get_guild(guild_id=1234567890)
        created_at = guild['created_at']
        updated_at = guild['updated_at']
        assert guild['name'] == 'Test Guild'
        
        mongo_client.update_guild(guild_id=1234567890, data={'name': 'Test Guild 2', 'new_value': 'new value'})
        updated_guild = mongo_client.get_guild(guild_id=1234567890)
        assert updated_guild['name'] == 'Test Guild 2'
        assert updated_guild['new_value'] == 'new value'
        assert updated_guild['created_at'] == created_at
        assert updated_guild['updated_at'] > updated_at
    
    def test_delete(self):
        mongo_client = MongoClient(host=pytest.mongo_host, port=pytest.mongo_port, username=pytest.mongo_username, password=pytest.mongo_password, auth_source=pytest.mongo_auth_source)
        assert mongo_client.get_guild(guild_id=1234567890) == {}
        mongo_client.delete_guild(guild_id=1234567890)
        assert mongo_client.get_guild(guild_id=1234567890) is None


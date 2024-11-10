# TODO: develop tests with https://testcontainers.com/modules/mongodb/
# TODO: add tests for mongo_client
import os
import pytest
from testcontainers.mongodb import MongoDbContainer
from src.mongo_client import MongoClient

mongo_container = MongoDbContainer("mongo:latest")

@pytest.fixture(scope="module", autouse=True)
def setup(request):
    mongo_container.start()

    def remove_container():
        mongo_container.stop()

    request.addfinalizer(remove_container)
    os.environ["MONGO_HOST"] = mongo_container.get_connection_url()
    os.environ["MONGO_PORT"] = str(mongo_container.get_port())
    os.environ["MONGO_USERNAME"] = mongo_container.MONGO_USERNAME
    os.environ["MONGO_PASSWORD"] = mongo_container.MONGO_PASSWORD
    os.environ["MONGO_DB"] = "discord_bot"

@pytest.fixture(scope="function", autouse=True)
def setup_data():
    pass

def test_mongo_client():
    with MongoDbContainer("mongo:latest") as mongo:
        mongo_client = MongoClient(host=mongo.get_host(), port=mongo.get_port(), username="root", password="example")
        db = mongo_client.get_db()
        collection = db.get_collection('guilds')
        assert collection.count_documents({}) == 0

        # TODO: add tests for update_guild
        # TODO: add tests for get_guild
        # TODO: add tests for get_collection
        # TODO: add tests for get_db
        # TODO: add tests for update_guild
        # TODO: add tests for delete_guild
        # TODO: add tests for get_guild_settings
        # TODO: add tests for update_guild_settings 
        # TODO: add tests for delete_guild_settings

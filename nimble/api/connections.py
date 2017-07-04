import json

from azure.storage.blob import BlockBlobService
import pymongo

from nimble.settings import BASE_DIR


def set_azure_connection():
    """
    Connect to Azure storage
    Use credentials from 'credentials.json'
    :return: BlockBlobService() (connection object)
    """
    with open(BASE_DIR + '\\credentials.json') as creds:
        creds_data = json.load(creds)
        account_name = creds_data['account_name']
        account_key = creds_data['account_key']

    return BlockBlobService(account_name=account_name, account_key=account_key)


def set_mongo_connection():
    """
    Connect to MongoDB
    :return: MongoDB collection object
    """
    mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
    mongo_collection = mongo_client.blob_links_storage.links
    return mongo_collection

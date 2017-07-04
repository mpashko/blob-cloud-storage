# To start Celery: celery -A nimble worker -l info
from __future__ import absolute_import, unicode_literals
from celery import shared_task

import time
import os

from nimble.settings import BASE_DIR
from .connections import set_azure_connection, set_mongo_connection


@shared_task
def upload_file_to_azure(filename):
    """
    Uploads the required file to Azure storage in the background
    :param filename: str
    :return: nothing
    """
    azure_connection = set_azure_connection()
    temp_storage_path = BASE_DIR + '\\temp_storage\\' + filename
    azure_connection.create_blob_from_path(container_name='container', blob_name=filename, file_path=temp_storage_path)

    time.sleep(20)

    change_file_status(filename)
    os.remove(temp_storage_path)


def change_file_status(filename):
    """
    Changes file field "open_to_read" from False to True in MongoDB
    :param filename: str
    :return: nothing
    """
    mongo_collection = set_mongo_connection()
    mongo_collection.update_one(
        {"filename": filename},
        {"$set": {
            "open_to_read": True
        }},
    )

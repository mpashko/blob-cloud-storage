import json
import os

from azure.storage.blob import BlockBlobService
from pymongo import MongoClient

from blob_storage.blob_storage.celery import app


class TemporaryStorage:
    """
    Storage for files until they are uploaded to the cloud
    """
    def __init__(self, path):
        """
        :param path: storage path
        :type path: str
        """
        self._path = path

    def save_file(self, blob):
        """
        :type blob:

        :return: None
        """
        path = self.get_file_path(blob.name)
        with open(path, 'wb+') as t_file:
            data = blob.read()
            t_file.write(data)

    def get_file_path(self, filename):
        """
        :type filename: str

        :rtype: str
        """
        return os.path.join(self._path, filename)

    @staticmethod
    def remove_file(path):
        """
        :type path: str

        :return: None
        """
        os.remove(path)

    def get_temporary_file(self, filename):
        """
        :type filename: str

        :rtype: str
        """
        path = self.get_file_path(filename)
        with open(path) as t_file:
            return t_file.read()


class ReportDAO:
    """
    Store reports for uploaded files
    """
    def __init__(self, connection_uri):
        """
        :param connection_uri: used to connect to a MongoDB. For details, please refer to
            https://docs.mongodb.com/manual/reference/connection-string/
        :type connection_uri: unicode
        """
        client = MongoClient(connection_uri)
        self._collection = client.blob_storage.reports

    def add_report(self, storage_name, filename):
        """
        :param filename: name of the stored file
        :type filename: unicode

        :param storage_name: storage where the file is located
        :type storage_name: unicode

        :return: None
        """
        self._collection.insert_one({
            'storage': storage_name,
            'filename': filename,
            'is_uploaded': False
        })

    def is_file_exists(self, filename):
        """
        Verifies that the requested file exists in the database

        :param filename: file to check
        :type filename: str

        :return: True if the file exists, otherwise False
        :rtype: bool
        """
        report = self.get_report(filename)
        return bool(report)

    def get_report(self, filename):
        """
        :type filename: str

        :rtype: dict[unicode, unicode | bool] | None
        """
        return self._collection.find_one({
            'filename': filename
        })

    def mark_as_uploaded(self, filename):
        """
        :param filename: uploaded file
        :type filename: str

        :return: None
        """
        self._collection.update_one(
            {'filename': filename},
            {'$set': {'is_uploaded': True}}
        )


class AzureClient:
    """
    Establishes a connection to Azure storage, uploads and retrieves files
    """
    def __init__(self, credential_path, temporary_storage, report_dao):
        """
        :param credential_path: path to Azure credential
        :type credential_path: str

        :param temporary_storage: dependency is used to get files from temporary storage
        :type temporary_storage: blob_storage.api.models.TemporaryStorage

        :param report_dao: dependency is used to control file upload status
        :type report_dao: blob_storage.api.models.ReportDAO
        """
        with open(credential_path) as credential:
            data = json.load(credential)
            account_name = data['account_name']
            account_key = data['account_key']

        self._connection = BlockBlobService(
            account_name=account_name,
            account_key=account_key
        )
        self._temporary_storage = temporary_storage
        self._report_dao = report_dao

    def upload_file(self, filename):
        """
        :param filename: file from temporary storage for upload
        :type filename: str

        :return: None
        """
        self._upload.delay(filename)

    @app.task()
    def _upload(self, filename):
        """
        Uploads the file, changes its status and remove it from the temporary storage

        :type filename: str

        :return: None
        """
        file_path = self._temporary_storage.get_file_path(filename)
        self._connection.create_blob_from_path(
            container_name='container',
            blob_name=filename,
            file_path=file_path
        )
        self._report_dao.mark_as_uploaded(filename)
        self._temporary_storage.remove_file(file_path)

    def get_file(self, filename):
        """
        :param filename: file to retrieve
        :type filename: str

        :return: saved file
        :rtype: azure.storage.blob.models.Blob
        """
        return self._connection.get_blob_to_bytes('container', filename)


class BlobModel:
    """
    Manages file upload cycle
    """
    def __init__(self, temporary_storage, report_dao, azure_client):
        """
        :param temporary_storage: dependency is used for temporary storage of files
        :type temporary_storage: blob_storage.api.models.TemporaryStorage

        :param report_dao: dependency is used to control file upload status
        :type report_dao: blob_storage.api.models.ReportDAO

        :param azure_client: dependency is used to upload files to Azure storage
        :type azure_client: blob_storage.api.models.AzureClient
        """
        self._temporary_storage = temporary_storage
        self._report_dao = report_dao
        self._azure_client = azure_client

    def is_file_exists(self, filename):
        """
        Verifies that the requested file exists in the database

        :param filename: file to check
        :type filename: str

        :return: True if the file exists, otherwise False
        :rtype: bool
        """
        return self._report_dao.is_file_exists(filename)

    def save_file(self, storage_name, blob):
        """
        :param storage_name: storage to save the file
        :type storage_name: unicode

        :param blob: file to upload
        :type blob:

        :return: None
        """
        self._temporary_storage.save_file(blob)
        filename = blob.name
        self._report_dao.add_report(storage_name, filename)
        self._azure_client.upload_file(filename)

    def get_file(self, filename):
        """
        :param filename:
        :type filename: str

        :return:
        :rtype: str | None
        """
        report = self._report_dao.get_report(filename)
        if report is None:
            return

        if report['is_uploaded']:
            blob = self._azure_client.get_file(filename)
            return blob.content

        return self._temporary_storage.get_temporary_file(filename)

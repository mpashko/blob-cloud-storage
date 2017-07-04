import os

from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from azure.storage.blob import BlockBlobService
import pymongo

from nimble.settings import BASE_DIR
from .serializers import UploadBlobSerializer


class MongoDBConnection(object):
    """
    Responsible for connection to MongoDB
    """
    connection = None

    def __get__(self, instance, owner):
        if not self.connection:
            mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
            self.connection = mongo_client.blob_links_storage.links
        return self.connection


class MongoDBStorage():
    """
    Provide access to MongoDB collection
    """
    mongo_collection = MongoDBConnection()


class FileUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request):
        up_file = request.FILES['file']
        temp_file = BASE_DIR + '\\temp_storage\\{}'.format(up_file.name)
        with open(temp_file, 'wb+') as file:
            data = up_file.read()
            file.write(data)
        return Response(status=status.HTTP_201_CREATED)


class BlobCreatorView(APIView, MongoDBStorage):
    """
    Responsible for binary files creation
    """
    def post(self, request):
        serializer = UploadBlobSerializer(data=request.data)
        if serializer.is_valid():
            filename, storage = serializer.data.values()

            upload_dir = BASE_DIR + '\\upload\\{}'.format(filename)
            if not os.path.exists(upload_dir):
                return Response('File not found', status=status.HTTP_400_BAD_REQUEST)

            if self._check_file_existance_in_db(filename):
                return Response('File with such name already exists', status=status.HTTP_409_CONFLICT)

            if storage.lower() == 'azure':
                # upload file to the server

                # make as Celery worker
                _upload_file_to_azure(filename, upload_dir)
            else:
                return Response('Not allowed storage', status=status.HTTP_400_BAD_REQUEST)

            self._add_to_db(filename, storage)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _check_file_existance_in_db(self, filename):
        """
        Check that required file exist in database
        :param filename: str
        :return: bool
        """
        return self.mongo_collection.find_one({"filename": filename})

    def _add_to_db(self, filename, storage):
        """
        Add link to binary file into MongoDB
        :param filename: str
        :param storage: str
        :return: nothing
        """
        self.mongo_collection.insert_one({
            "filename": filename,
            "storage": storage
        })


class BlobContentView(APIView, MongoDBStorage):
    """
    Return binary file content in response
    """
    def get(self, request, filename):
        file = self.mongo_collection.find_one({"filename": filename})
        if not file:
            return Response('File not found', status=status.HTTP_400_BAD_REQUEST)

        if file['storage'].lower() == 'azure':
            azure_connection = _set_azure_connection()
            blob = azure_connection.get_blob_to_bytes('container', filename)
            return Response(blob.content, status=status.HTTP_200_OK)


def _set_azure_connection():
    """
    Connect to Azure storage
    :return: BlockBlobService() (connection object)
    """
    account_name = os.environ['ACCOUNT_NAME']
    account_key = os.environ['ACCOUNT_KEY']
    return BlockBlobService(account_name=account_name, account_key=account_key)


def _upload_file_to_azure(filename, upload_dir):
    """
    Upload required file to Azure storage
    :param filename: str
    :param upload_dir: str (path to file)
    :return: nothing
    """
    azure_connection = _set_azure_connection()
    azure_connection.create_blob_from_path(container_name='container', blob_name=filename, file_path=upload_dir)

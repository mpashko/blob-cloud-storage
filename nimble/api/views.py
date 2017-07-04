from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
import pymongo

from nimble.settings import BASE_DIR
from .tasks import upload_file_to_azure
from .connections import set_azure_connection


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


class BlobCreatorView(APIView, MongoDBStorage):
    """
    Responsible for binary files creation
    """
    parser_classes = (FileUploadParser,)
    STORAGE_LIST = ['azure']

    def post(self, request):
        up_file = request.FILES.get('file')
        if not up_file:
            return Response('No file to upload', status=status.HTTP_400_BAD_REQUEST)

        storage = request.query_params.get('storage')
        allowed_storage = storage.lower() in self.STORAGE_LIST
        if not storage or not allowed_storage:
            return Response('Check "storage" parameter', status=status.HTTP_400_BAD_REQUEST)

        filename = up_file.name
        if self._check_file_existance_in_db(filename):
            return Response('File with such name already exists', status=status.HTTP_409_CONFLICT)

        _save_file_to_temporary_storage(up_file)

        self._add_to_db(filename, storage)

        if storage.lower() == 'azure':
            upload_file_to_azure.delay(filename)

        return Response(status=status.HTTP_201_CREATED)

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
            "storage": storage,
            "open_to_read": False
        })


class BlobContentView(APIView, MongoDBStorage):
    """
    Returns a binary file content in response.
    While file is uploaded to cloud storage,
    returns data from a temporary storage on the server.
    """
    def get(self, request, filename):
        file = self.mongo_collection.find_one({"filename": filename})
        if not file:
            return Response('File not found', status=status.HTTP_400_BAD_REQUEST)

        if not file['open_to_read']:
            with open(BASE_DIR + '\\temp_storage\\' + filename) as file:
                file_data = file.read()
            return Response(file_data, status=status.HTTP_200_OK)

        if file['storage'].lower() == 'azure':
            azure_connection = set_azure_connection()
            blob = azure_connection.get_blob_to_bytes('container', filename)
            return Response(blob.content, status=status.HTTP_200_OK)


def _save_file_to_temporary_storage(file_to_save):
    """
    Save a file to a temporary storage
    :param file_to_save: str
    :return: nothing
    """
    filename = file_to_save.name
    temp_file = BASE_DIR + '\\temp_storage\\{}'.format(filename)
    with open(temp_file, 'wb+') as file:
        data = file_to_save.read()
        file.write(data)

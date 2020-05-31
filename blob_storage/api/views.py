from rest_framework import status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .application import BLOB_MODEL


class BlobUploaderView(APIView):

    parser_classes = (FileUploadParser,)
    _STORAGE_LIST = ['azure']

    def post(self, request):
        blob = request.FILES.get('file')
        if not blob:
            return Response('No file to upload', status=status.HTTP_409_CONFLICT)

        storage_name = request.query_params.get('storage')
        if not storage_name:
            return Response('Storage not specified', status=status.HTTP_409_CONFLICT)

        is_storage_allowed = storage_name.lower() in self._STORAGE_LIST
        if not is_storage_allowed:
            return Response('Unsupported storage specified', status=status.HTTP_409_CONFLICT)

        if BLOB_MODEL.is_file_exists(blob.name):
            return Response('A file with the same name already exists', status=status.HTTP_409_CONFLICT)

        BLOB_MODEL.save_file(storage_name, blob)
        return Response(status=status.HTTP_201_CREATED)


class BlobContentView(APIView):
    """
    While a file is uploaded to a cloud storage, returns data from a temporary storage on the server
    """
    def get(self, request, filename):
        content = BLOB_MODEL.get_file(filename)
        if content is None:
            return Response('File not found', status=status.HTTP_404_NOT_FOUND)

        return Response(content, status=status.HTTP_200_OK)

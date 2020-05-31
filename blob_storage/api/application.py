import os

from blob_storage.settings import BASE_DIR

from blob_storage.api.models import TemporaryStorage, ReportDAO, AzureClient, BlobModel

__all__ = ('BLOB_MODEL',)

_TEMPORARY_STORAGE = TemporaryStorage(path=os.path.join(BASE_DIR, 'temporary_storage'))

_REPORT_DAO = ReportDAO(connection_uri='mongodb://localhost:27017')

_AZURE_CLIENT = AzureClient(
    credential_path=os.path.join(BASE_DIR, 'credentials.json'),
    temporary_storage=_TEMPORARY_STORAGE,
    report_dao=_REPORT_DAO
)

BLOB_MODEL = BlobModel(_TEMPORARY_STORAGE, _REPORT_DAO, _AZURE_CLIENT)

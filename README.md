# REST API for cloud storage

Current app allow to upload and review binary files from different cloud storages. Current it works only with Microsoft Azure Storage.
All references to uploaded files stores in MongoDB. The app works with MongoDB all the time in order to receive an information in what cloud storage located the required file.

At the moment, there are implemented the following endpoints:
```
POST /api/blobs
{
  "filename": name of the file, that should be uploaded,
  "storage": name of the cloud storage, where the file will be located
}
```
Mentioned endpoint allow to upload needed file to cloud storage ('azure' currently).
Current service designed as immutable storage. It is mean that uploaded to cloud files cann't be changed and updated.
If neccessary, it should be created with another file name.

```
GET /api/blobs/<filename>
```
Return the value of the required file. App defined where it is store by itself.

More specific information, related to class responsibilities mention into docstrings.

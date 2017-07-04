# REST API for cloud storage

Current app allow to upload and review binary files from different cloud storages. At the moment, it works only with Microsoft Azure Storage.
All references to uploaded files stores in MongoDB. The app works with MongoDB all the time in order to receive an information in what cloud storage located the required file.

At the moment, there are implemented the following endpoints:
```
POST /api/blobs?storage=<storage>
Headers [
  {"key":"Content-Disposition","value":"form-data; filename='<filename>'"},
  {"key":"Content-Type","value":"application/octet-stream"}
]

Body [
  <binary file>
]

<storage> -- name of the cloud storage where the file will be located
<filename> -- name of the file that should be uploaded
<binary file> -- the file that should be uploaded
```

Mentioned endpoint allow to upload needed file to cloud storage ('azure' currently).
Current service designed as immutable storage. It is mean that uploaded to cloud files cann't be changed and updated.
If neccessary, it should be created with another file name.

```
GET /api/blobs/<filename>
```
Return the value of the required file. App define where it is stores by itself.

More specific information, related to class responsibilities mention into docstrings.

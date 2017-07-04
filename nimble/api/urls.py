from django.conf.urls import url

from .views import BlobCreatorView, BlobContentView, FileUploadView

urlpatterns = [
    url(r'^blobs$', BlobCreatorView.as_view()),
    url(r'^blobs/(?P<filename>[\w]+)/$', BlobContentView.as_view()),
    url(r'^upload$', FileUploadView.as_view())
]

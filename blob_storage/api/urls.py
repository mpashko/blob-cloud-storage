from django.conf.urls import url

from .views import BlobUploaderView, BlobContentView

urlpatterns = [
    url(r'^blobs$', BlobUploaderView.as_view()),
    url(r'^blobs/(?P<filename>[\w]+)/$', BlobContentView.as_view()),
]

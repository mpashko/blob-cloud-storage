from django.conf.urls import url

from .views import BlobCreator, BlobContent

urlpatterns = [
    url(r'^blobs$', BlobCreator.as_view()),
    url(r'^blobs/(?P<filename>[\w]+)/$', BlobContent.as_view()),
]

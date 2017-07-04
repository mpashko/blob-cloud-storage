from django.conf.urls import url

from .views import BlobCreatorView, BlobContentView

urlpatterns = [
    url(r'^blobs$', BlobCreatorView.as_view()),
    url(r'^blobs/(?P<filename>[\w]+)/$', BlobContentView.as_view()),
]

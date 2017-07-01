from rest_framework import serializers


class UploadBlobSerializer(serializers.Serializer):
    filename = serializers.CharField(required=True, allow_blank=False, max_length=100)
    storage = serializers.CharField(required=True, allow_blank=False, max_length=100)

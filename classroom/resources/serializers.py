from rest_framework import serializers

from .models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = (
            'id', 'topic', 'title', 'resource_type',
            'size_label', 'description', 'file_url', 'created_at',
        )
        read_only_fields = ('id', 'created_at')

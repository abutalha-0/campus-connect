from rest_framework import serializers

from classroom.access import can_modify_content

from .models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = (
            'id', 'title', 'resource_type',
            'description', 'file_url', 'created_at', 'can_edit',
        )
        read_only_fields = ('id', 'created_at', 'can_edit')

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return can_modify_content(request.user, obj.subject, obj.author_id)

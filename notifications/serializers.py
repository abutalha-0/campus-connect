from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'actor', 'notification_type', 'post', 'post_title',
            'join_request', 'message', 'action_url', 'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = fields

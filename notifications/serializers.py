from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    post_title = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'actor', 'notification_type', 'post', 'post_title',
            'join_request', 'lost_found_item', 'claim_attempt',
            'message', 'action_url', 'is_read', 'read_at', 'created_at',
        ]
        read_only_fields = fields

    def get_post_title(self, obj):
        if obj.post:
            return obj.post.title
        if obj.lost_found_item:
            return obj.lost_found_item.title
        return None

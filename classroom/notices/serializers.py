from rest_framework import serializers

from classroom.access import can_modify_content, author_role_label

from .models import Notice


class NoticeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    mine = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    has_highlight = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = ('id', 'text', 'highlight', 'event_date', 'event_time',
                  'attachment_url', 'created_at', 'author', 'mine', 'can_edit',
                  'has_highlight')
        read_only_fields = ('id', 'created_at', 'attachment_url', 'author', 'mine',
                            'can_edit', 'has_highlight')

    def validate(self, data):
        event_time = data.get('event_time', getattr(self.instance, 'event_time', None))
        event_date = data.get('event_date', getattr(self.instance, 'event_date', None))
        if event_time and not event_date:
            raise serializers.ValidationError(
                {'event_time': 'event_time requires event_date to also be set.'}
            )
        return data

    def get_has_highlight(self, obj):
        """True if the notice should show a highlighted callout — free-text
        label and/or the structured date/time, either alone is enough."""
        return bool(obj.highlight or obj.event_date)

    def get_author(self, obj):
        return {
            'id': obj.author_id,
            'full_name': obj.author.full_name,
            'role': author_role_label(obj.author),
        }

    def get_mine(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.id == obj.author_id)

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return can_modify_content(request.user, obj.subject, obj.author_id)

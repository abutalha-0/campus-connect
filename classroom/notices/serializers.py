from rest_framework import serializers

from classroom.access import can_modify_content

from .models import Notice


def author_role_label(user):
    """
    The badge shown next to a notice author: FACULTY, CR (a student who is a
    class representative), or STUDENT.
    """
    if getattr(user, 'role', None) == 'FACULTY':
        return 'FACULTY'
    student_profile = getattr(user, 'student_profile', None)
    if student_profile and student_profile.user_type == 'CR':
        return 'CR'
    return 'STUDENT'


class NoticeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    mine = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = ('id', 'text', 'highlight', 'attachment_url', 'created_at',
                  'author', 'mine', 'can_edit')
        read_only_fields = ('id', 'created_at', 'attachment_url', 'author', 'mine', 'can_edit')

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

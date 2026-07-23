from rest_framework import serializers

from classroom.access import author_role_label
from classroom.notices.models import Notice


class ScheduleEventSerializer(serializers.ModelSerializer):
    """
    A dated notice, reshaped for the auto-collected Schedule view. Not a
    separate model — Schedule is purely a query over Notice rows that have
    event_date set, across every subject in the student's class.
    """
    notice_id = serializers.IntegerField(source='id', read_only=True)
    subject_id = serializers.IntegerField(read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    title = serializers.SerializerMethodField()
    author_role = serializers.SerializerMethodField()

    class Meta:
        model = Notice
        fields = (
            'notice_id', 'subject_id', 'subject_name',
            'title', 'event_date', 'event_time', 'author_role',
        )

    def get_title(self, obj):
        # The highlight label is the intended short title; a notice can have
        # a date without one, so fall back to a snippet of the body.
        if obj.highlight:
            return obj.highlight
        text = (obj.text or '').strip()
        return text if len(text) <= 60 else text[:57] + '…'

    def get_author_role(self, obj):
        return author_role_label(obj.author)

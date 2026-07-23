from rest_framework import serializers

from classroom.access import is_subject_faculty, can_post_to_subject

from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.user.full_name', read_only=True)
    # Tell the client whether the current viewer owns this subject (faculty —
    # can access settings/update/delete) and whether they may post content
    # (faculty owner or the CR of a class containing this subject).
    is_owner = serializers.SerializerMethodField()
    can_post = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = (
            'id', 'name', 'intake', 'section', 'room',
            'code', 'faculty_name', 'is_owner', 'can_post', 'created_at',
        )
        read_only_fields = (
            'id', 'code', 'faculty_name', 'is_owner', 'can_post', 'created_at'
        )

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and is_subject_faculty(request.user, obj))

    def get_can_post(self, obj):
        request = self.context.get('request')
        return bool(request and can_post_to_subject(request.user, obj))

    def create(self, validated_data):
        validated_data['code'] = Subject.generate_unique_code()
        return super().create(validated_data)

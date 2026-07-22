from rest_framework import serializers

from classroom.subjects.serializers import SubjectSerializer

from .models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    is_creator = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = ('id', 'code', 'subjects', 'is_creator', 'created_at')
        read_only_fields = ('id', 'code', 'subjects', 'is_creator', 'created_at')

    def get_is_creator(self, obj):
        request = self.context.get('request')
        return bool(request and obj.creator_id == request.user.id)

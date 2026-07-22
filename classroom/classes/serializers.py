from rest_framework import serializers

from classroom.subjects.serializers import SubjectSerializer

from .models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Classroom
        fields = ('id', 'code', 'subjects', 'created_at')
        read_only_fields = ('id', 'code', 'subjects', 'created_at')

from rest_framework import serializers

from classroom.subjects.serializers import SubjectSerializer

from .models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    is_creator = serializers.SerializerMethodField()
    creator_id = serializers.IntegerField(read_only=True)
    creator_name = serializers.CharField(source='creator.full_name', read_only=True)

    class Meta:
        model = Classroom
        fields = ('id', 'code', 'subjects', 'is_creator', 'creator_id', 'creator_name', 'created_at')
        read_only_fields = (
            'id', 'code', 'subjects', 'is_creator', 'creator_id', 'creator_name', 'created_at'
        )

    def get_is_creator(self, obj):
        request = self.context.get('request')
        return bool(request and obj.creator_id == request.user.id)

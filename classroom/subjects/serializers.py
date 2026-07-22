from rest_framework import serializers

from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.user.full_name', read_only=True)

    class Meta:
        model = Subject
        fields = (
            'id', 'name', 'intake', 'section', 'room',
            'code', 'faculty_name', 'created_at',
        )
        read_only_fields = ('id', 'code', 'faculty_name', 'created_at')

    def create(self, validated_data):
        validated_data['code'] = Subject.generate_unique_code()
        return super().create(validated_data)

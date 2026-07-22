import re

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import FacultyProfile

User = get_user_model()


def generate_unique_username(email):
    """
    Faculty sign-up has no username field, so we derive one from the email
    local-part. Kept within User.username's max_length and made unique by
    appending a numeric suffix when needed. Faculty never see this value.
    """
    local_part = email.split('@')[0]
    base = re.sub(r'[^a-zA-Z0-9_.]', '', local_part).lower() or 'faculty'
    base = base[:30]

    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix_str = str(suffix)
        username = base[:30 - len(suffix_str)] + suffix_str
        suffix += 1
    return username


class FacultyRegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    employee_id = serializers.CharField(max_length=50)
    department = serializers.CharField(max_length=100)
    designation = serializers.ChoiceField(choices=FacultyProfile.DESIGNATION_CHOICES)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_employee_id(self, value):
        if FacultyProfile.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("This employee ID is already registered.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=generate_unique_username(validated_data['email']),
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            role='FACULTY',
        )
        faculty_profile = FacultyProfile.objects.create(
            user=user,
            employee_id=validated_data['employee_id'],
            department=validated_data['department'],
            designation=validated_data['designation'],
        )
        return user, faculty_profile


class FacultyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyProfile
        fields = ('employee_id', 'department', 'designation', 'is_verified')

import re
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from shared.link_platforms import SINGLE_INSTANCE_LINK_PLATFORMS, PLATFORM_DOMAINS

from .models import FacultyProfile, FacultyLink

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


# ─── Links ────────────────────────────────────────────────────────────────────

class FacultyLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyLink
        fields = ('id', 'link_name', 'icon', 'url')

    def validate_icon(self, value):
        icon = (value or '').lower()
        faculty = self.context.get('faculty')
        if faculty and icon in SINGLE_INSTANCE_LINK_PLATFORMS:
            if FacultyLink.objects.filter(faculty=faculty, icon__iexact=icon).exists():
                raise serializers.ValidationError(
                    f"You've already added a {icon.capitalize()} link. Remove it first to add another."
                )
        return value

    def validate(self, attrs):
        icon = (attrs.get('icon') or '').lower()
        domains = PLATFORM_DOMAINS.get(icon)
        if domains:
            host = urlparse(attrs.get('url') or '').netloc.lower()
            if not any(host == d or host.endswith('.' + d) for d in domains):
                raise serializers.ValidationError(
                    {'url': f"Enter a {icon.capitalize()} link (must be a {domains[0]} URL)."}
                )
        return attrs


# ─── Faculty "me" (own profile view/edit) ─────────────────────────────────────

class FacultyBaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email')


class FacultyMeSerializer(serializers.ModelSerializer):
    user = FacultyBaseUserSerializer(read_only=True)
    links = FacultyLinkSerializer(many=True, read_only=True)

    # Editable identity field that lives on the related User, surfaced here so
    # the "edit identity" screen can update it in the same PATCH.
    full_name = serializers.CharField(
        source='user.full_name', required=False, max_length=100
    )

    class Meta:
        model = FacultyProfile
        fields = (
            'user',
            'full_name',
            'employee_id',
            'department',
            'designation',
            'is_verified',
            'profile_photo',
            'updated_at',
            'links',
        )
        # email is intentionally read-only (it is the login identifier);
        # employee_id / is_verified are not user-editable here.
        read_only_fields = ('user', 'employee_id', 'is_verified', 'updated_at')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data and 'full_name' in user_data:
            instance.user.full_name = user_data['full_name']
            instance.user.save(update_fields=['full_name'])
        return super().update(instance, validated_data)


# ─── Faculty public profile (viewed by other users) ────────────────────────────

class FacultyPublicProfileSerializer(serializers.ModelSerializer):
    user = FacultyBaseUserSerializer(read_only=True)
    links = FacultyLinkSerializer(many=True, read_only=True)
    subjects = serializers.SerializerMethodField()

    class Meta:
        model = FacultyProfile
        fields = (
            'user',
            'department',
            'designation',
            'profile_photo',
            'links',
            'subjects',
            # employee_id and is_verified are intentionally excluded — not
            # meant for other users to see.
        )

    def get_subjects(self, obj):
        # The subject's share `code` is a secret for enrollment — never
        # exposed here, so this can't be built from SubjectSerializer.
        return [
            {'id': s.id, 'name': s.name, 'intake': s.intake, 'section': s.section}
            for s in obj.subjects.all()
        ]

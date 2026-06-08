from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Profile,
    LookingFor,
    Link,
    Education,
    Experience,
    Project,
    ProjectImage,
    Skill,
    UserSkill,
)

User = get_user_model()


# ─── Sub-model Serializers ────────────────────────────────────────────────────

class LookingForSerializer(serializers.ModelSerializer):
    class Meta:
        model = LookingFor
        fields = ('id', 'value')


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ('id', 'link_name', 'icon', 'url')


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ('id', 'institution_name', 'degree', 'start_year', 'end_year', 'image_url')


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ('id', 'title', 'organization', 'description', 'start_date', 'end_date')


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ('id', 'image_url', 'is_cover', 'position', 'uploaded_at')
        read_only_fields = ('uploaded_at',)


class ProjectSerializer(serializers.ModelSerializer):
    images = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'associated_with', 'created_at', 'images')
        read_only_fields = ('created_at',)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('id', 'name', 'is_predefined')


class UserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        write_only=True
    )

    class Meta:
        model = UserSkill
        fields = ('id', 'skill', 'skill_id', 'proficiency')


# ─── Base User Info ───────────────────────────────────────────────────────────

class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name')


# ─── Public Profile Serializer (viewing another user's profile) ───────────────

class PublicProfileSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer(read_only=True)
    looking_for = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'user',
            'bio',
            'about',
            'user_type',
            'profile_photo',
            'looking_for',
            'links',
            'education',
            'experience',
            'projects',
            'skills',
            # dob and gender are intentionally excluded
        )

    def get_looking_for(self, obj):
        return LookingForSerializer(
            LookingFor.objects.filter(user=obj.user), many=True
        ).data

    def get_links(self, obj):
        return LinkSerializer(
            Link.objects.filter(user=obj.user), many=True
        ).data

    def get_education(self, obj):
        return EducationSerializer(
            Education.objects.filter(user=obj.user), many=True
        ).data

    def get_experience(self, obj):
        return ExperienceSerializer(
            Experience.objects.filter(user=obj.user), many=True
        ).data

    def get_projects(self, obj):
        return ProjectSerializer(
            Project.objects.filter(user=obj.user), many=True
        ).data

    def get_skills(self, obj):
        return UserSkillSerializer(
            UserSkill.objects.filter(user=obj.user), many=True
        ).data


# ─── Private Profile Serializer (viewing/editing own profile) ─────────────────

class PrivateProfileSerializer(serializers.ModelSerializer):
    user = BaseUserSerializer(read_only=True)
    looking_for = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'user',
            'bio',
            'about',
            'dob',           # private — only visible to owner
            'gender',        # private — only visible to owner
            'user_type',
            'profile_photo',
            'updated_at',
            'looking_for',
            'links',
            'education',
            'experience',
            'projects',
            'skills',
        )
        read_only_fields = ('user', 'updated_at')

    def get_looking_for(self, obj):
        return LookingForSerializer(
            LookingFor.objects.filter(user=obj.user), many=True
        ).data

    def get_links(self, obj):
        return LinkSerializer(
            Link.objects.filter(user=obj.user), many=True
        ).data

    def get_education(self, obj):
        return EducationSerializer(
            Education.objects.filter(user=obj.user), many=True
        ).data

    def get_experience(self, obj):
        return ExperienceSerializer(
            Experience.objects.filter(user=obj.user), many=True
        ).data

    def get_projects(self, obj):
        return ProjectSerializer(
            Project.objects.filter(user=obj.user), many=True
        ).data

    def get_skills(self, obj):
        return UserSkillSerializer(
            UserSkill.objects.filter(user=obj.user), many=True
        ).data
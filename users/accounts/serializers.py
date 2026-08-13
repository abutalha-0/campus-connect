from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name', 'password')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'full_name', 'role', 'bio', 'created_at')
        read_only_fields = ('id', 'email', 'role', 'created_at')


class DiscoverUserSerializer(serializers.ModelSerializer):
    """User list/search for the Discover screen. Adds the profile-photo and
    role-specific fields UserSerializer intentionally omits (Discover needs
    them for its cards; nothing else that reuses UserSerializer does), read
    from the profile relations UserListView.get_queryset() select_relates so
    this stays one query regardless of list size.
    """
    profile_photo = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'full_name', 'role', 'bio',
            'profile_photo', 'user_type', 'designation', 'department',
        )

    def get_profile_photo(self, obj):
        if obj.role == 'FACULTY':
            profile = getattr(obj, 'faculty_profile', None)
        else:
            profile = getattr(obj, 'student_profile', None)
        return profile.profile_photo if profile and profile.profile_photo else None

    def get_user_type(self, obj):
        if obj.role != 'STUDENT':
            return None
        profile = getattr(obj, 'student_profile', None)
        return profile.user_type if profile else None

    def get_designation(self, obj):
        if obj.role != 'FACULTY':
            return None
        profile = getattr(obj, 'faculty_profile', None)
        return profile.designation if profile else None

    def get_department(self, obj):
        if obj.role != 'FACULTY':
            return None
        profile = getattr(obj, 'faculty_profile', None)
        return profile.department if profile else None
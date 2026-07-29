from rest_framework import serializers

from users.accounts.serializers import UserSerializer
from users.student_profile.models import Skill

from .models import Bookmark, Category, JoinRequest, Post, PostMember
from .validators import validate_post_details


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        source='skills', many=True, queryset=Skill.objects.all(), write_only=True, required=False
    )
    skills = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)
    accepted_members_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'category', 'category_detail', 'title', 'slug', 'status',
            'description', 'location', 'contact_info', 'details', 'skills', 'skill_ids',
            'max_members', 'accepted_members_count', 'is_full', 'deadline', 'is_featured',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'status', 'created_at', 'updated_at']

    def validate(self, attrs):
        category = attrs.get('category') or getattr(self.instance, 'category', None)
        details = attrs.get('details', getattr(self.instance, 'details', {}))
        if category is not None:
            validate_post_details(category.slug, details)
        return attrs

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class JoinRequestSerializer(serializers.ModelSerializer):
    requester = UserSerializer(read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = JoinRequest
        fields = [
            'id', 'post', 'post_title', 'requester', 'message', 'status',
            'reviewed_by', 'reviewed_at', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'reviewed_by', 'reviewed_at', 'created_at']

    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)


class PostMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = PostMember
        fields = ['id', 'post', 'user', 'joined_at']


class BookmarkSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'post', 'post_title', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

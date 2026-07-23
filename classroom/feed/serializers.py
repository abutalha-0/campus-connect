from rest_framework import serializers

from classroom.access import author_role_label

from .models import FeedPost, FeedComment


class FeedCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = FeedComment
        fields = ('id', 'text', 'created_at', 'author', 'can_edit')
        read_only_fields = ('id', 'created_at', 'author', 'can_edit')

    def get_author(self, obj):
        return {
            'id': obj.author_id,
            'full_name': obj.author.full_name,
            'role': author_role_label(obj.author),
        }

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.id == obj.author_id)


class FeedPostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    my_vote = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = FeedPost
        fields = (
            'id', 'tag', 'title', 'body', 'created_at',
            'author', 'can_edit', 'score', 'my_vote', 'comments_count',
        )
        read_only_fields = (
            'id', 'created_at', 'author', 'can_edit', 'score', 'my_vote', 'comments_count'
        )

    def get_author(self, obj):
        return {
            'id': obj.author_id,
            'full_name': obj.author.full_name,
            'role': author_role_label(obj.author),
        }

    def get_can_edit(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.id == obj.author_id)

    def get_score(self, obj):
        return sum(v.value for v in obj.votes.all())

    def get_my_vote(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        for v in obj.votes.all():
            if v.user_id == request.user.id:
                return v.value
        return 0

    def get_comments_count(self, obj):
        return obj.comments.count()

    def validate_tag(self, value):
        value = value.strip()
        if not value:
            return value

        classroom = self.context.get('classroom')
        valid_tags = set()
        if classroom is not None:
            for subject in classroom.subjects.all():
                valid_tags.add(subject.name)
                valid_tags.add(subject.faculty.user.full_name)

        if value not in valid_tags:
            raise serializers.ValidationError(
                'Choose a subject or faculty from your class, or leave this blank.'
            )
        return value

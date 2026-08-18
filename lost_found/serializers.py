from rest_framework import serializers

from .models import LostFoundItem, ClaimQuestion, ClaimAttempt, ClaimAnswer


class ClaimQuestionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimQuestion
        fields = ('id', 'question_text')


class ClaimQuestionOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimQuestion
        fields = ('id', 'question_text', 'correct_answer')


class ClaimQuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimQuestion
        fields = ('id', 'question_text', 'correct_answer')


class ClaimAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)

    class Meta:
        model = ClaimAnswer
        fields = ('id', 'question', 'question_text', 'answer_text')


class ClaimAttemptSerializer(serializers.ModelSerializer):
    claimant_username = serializers.CharField(source='claimant.username', read_only=True)
    answers = ClaimAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = ClaimAttempt
        fields = (
            'id',
            'item',
            'claimant',
            'claimant_username',
            'status',
            'submitted_at',
            'reviewed_at',
            'answers',
        )
        read_only_fields = ('id', 'item', 'claimant', 'status', 'submitted_at', 'reviewed_at')


class LostFoundItemPublicSerializer(serializers.ModelSerializer):
    reported_by = serializers.CharField(source='user.username', read_only=True)
    claim_questions = ClaimQuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = LostFoundItem
        fields = (
            'id',
            'title',
            'description',
            'item_type',
            'category',
            'location',
            'image_url',
            'contact_info',
            'event_date',
            'status',
            'reported_by',
            'created_at',
            'updated_at',
            'resolved_at',
            'claim_questions',
        )
        read_only_fields = ('id', 'reported_by', 'created_at', 'updated_at', 'resolved_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') and request.user.is_authenticated else None
        is_owner = (user and user == instance.user)
        is_approved_claimant = (
            user and
            instance.claim_attempts.filter(claimant=user, status='APPROVED').exists()
        )
        if instance.item_type == 'FOUND' and not (is_owner or is_approved_claimant):
            data['description'] = ""
            data['location'] = ""
            data['contact_info'] = ""
        return data


class LostFoundItemOwnerSerializer(serializers.ModelSerializer):
    reported_by = serializers.CharField(source='user.username', read_only=True)
    claim_questions = ClaimQuestionOwnerSerializer(many=True, read_only=True)
    claim_attempts = ClaimAttemptSerializer(many=True, read_only=True)

    class Meta:
        model = LostFoundItem
        fields = (
            'id',
            'title',
            'description',
            'item_type',
            'category',
            'location',
            'image_url',
            'contact_info',
            'event_date',
            'status',
            'reported_by',
            'created_at',
            'updated_at',
            'resolved_at',
            'claim_questions',
            'claim_attempts',
        )
        read_only_fields = ('id', 'reported_by', 'created_at', 'updated_at', 'resolved_at')


# Default alias for backward compatibility
LostFoundItemSerializer = LostFoundItemPublicSerializer


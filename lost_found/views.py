from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shared.cloudinary_utils import upload_image
from .models import LostFoundItem, ClaimQuestion, ClaimAttempt, ClaimAnswer
from .serializers import (
    LostFoundItemPublicSerializer,
    LostFoundItemOwnerSerializer,
    ClaimQuestionOwnerSerializer,
    ClaimAttemptSerializer,
)


class LostFoundItemListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        items = LostFoundItem.objects.all()
        item_type = request.query_params.get('item_type')
        status_filter = request.query_params.get('status')
        category = request.query_params.get('category')
        location = request.query_params.get('location')
        date = request.query_params.get('date')
        search = request.query_params.get('search')

        if item_type in ('LOST', 'FOUND'):
            items = items.filter(item_type=item_type)

        if category:
            items = items.filter(category__icontains=category)

        if location:
            items = items.filter(location__icontains=location)

        if date:
            items = items.filter(event_date=date)

        if status_filter:
            status_value = status_filter.upper()
            if status_value in dict(LostFoundItem.STATUS_CHOICES):
                items = items.filter(status=status_value)
        else:
            items = items.exclude(status='CLOSED')

        if search:
            items = items.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search) |
                Q(category__icontains=search)
            )

        return items

    def get(self, request):
        items = self.get_queryset(request)
        serializer = LostFoundItemPublicSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        if 'image' in request.FILES:
            data['image_url'] = upload_image(
                request.FILES['image'],
                folder='campus_connect/lost_found'
            )

        if 'event_date' not in data and 'date_seen' in data:
            data['event_date'] = data['date_seen']

        serializer = LostFoundItemPublicSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            item = serializer.save(user=request.user)
            return Response(
                LostFoundItemOwnerSerializer(item, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LostFoundItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)
        if item.user == request.user:
            serializer = LostFoundItemOwnerSerializer(item, context={'request': request})
        else:
            serializer = LostFoundItemPublicSerializer(item, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)
        if item.user != request.user and not request.user.is_staff:
            return Response({'detail': 'You can only update your own posts.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        if 'image' in request.FILES:
            data['image_url'] = upload_image(
                request.FILES['image'],
                folder='campus_connect/lost_found'
            )

        if 'event_date' not in data and 'date_seen' in data:
            data['event_date'] = data['date_seen']

        new_status = data.get('status')
        if new_status in ('CLAIMED', 'CLOSED') and item.status != new_status:
            if not item.resolved_at:
                item.resolved_at = timezone.now()

        serializer = LostFoundItemOwnerSerializer(item, data=data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            if new_status in ('CLAIMED', 'CLOSED') and item.resolved_at:
                item.save(update_fields=['resolved_at'])
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)
        if item.user != request.user and not request.user.is_staff:
            return Response({'detail': 'You can only delete your own posts.'}, status=status.HTTP_403_FORBIDDEN)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyLostFoundItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = LostFoundItem.objects.filter(user=request.user)
        serializer = LostFoundItemOwnerSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)


class ClaimQuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)

        if item.item_type != 'FOUND':
            return Response(
                {'detail': 'Claim questions can only be added to FOUND items.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if item.user != request.user:
            return Response(
                {'detail': 'Only the item owner can add claim questions.'},
                status=status.HTTP_403_FORBIDDEN
            )

        questions_data = request.data
        if isinstance(questions_data, dict):
            questions_data = [questions_data]

        created_questions = []
        for q_data in questions_data:
            q_text = q_data.get('question_text', '').strip()
            c_ans = q_data.get('correct_answer', '').strip()
            if not q_text or not c_ans:
                return Response(
                    {'detail': 'Both question_text and correct_answer are required for each question.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            question = ClaimQuestion.objects.create(
                item=item,
                question_text=q_text,
                correct_answer=c_ans
            )
            created_questions.append(question)

        serializer = ClaimQuestionOwnerSerializer(created_questions, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClaimAttemptView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)
        if item.user == request.user:
            attempts = ClaimAttempt.objects.filter(item=item)
        else:
            attempts = ClaimAttempt.objects.filter(item=item, claimant=request.user)

        serializer = ClaimAttemptSerializer(attempts, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, pk):
        item = get_object_or_404(LostFoundItem, id=pk)

        if item.item_type != 'FOUND':
            return Response(
                {'detail': 'Claim attempts can only be submitted for FOUND items.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if item.status != 'OPEN':
            return Response(
                {'detail': 'Item is not open for claims.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if item.user == request.user:
            return Response(
                {'detail': 'You cannot submit a claim attempt on your own item.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if ClaimAttempt.objects.filter(item=item, claimant=request.user).exists():
            return Response(
                {'detail': 'You have already submitted a claim attempt for this item.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        answers_data = request.data.get('answers', [])
        if not answers_data and isinstance(request.data, list):
            answers_data = request.data

        with transaction.atomic():
            attempt = ClaimAttempt.objects.create(
                item=item,
                claimant=request.user,
                status='PENDING'
            )
            for ans in answers_data:
                question_id = ans.get('question') or ans.get('question_id')
                answer_text = ans.get('answer_text', '').strip()
                question = get_object_or_404(ClaimQuestion, id=question_id, item=item)
                ClaimAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    answer_text=answer_text
                )

        serializer = ClaimAttemptSerializer(attempt, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClaimAttemptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        attempt = get_object_or_404(ClaimAttempt, id=pk)
        item = attempt.item

        if item.user != request.user:
            return Response(
                {'detail': 'Only the item owner can review claim attempts.'},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status', '').upper()
        if new_status not in ('APPROVED', 'REJECTED'):
            return Response(
                {'detail': 'Status must be APPROVED or REJECTED.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()
        with transaction.atomic():
            attempt.status = new_status
            attempt.reviewed_at = now
            attempt.save()

            if new_status == 'APPROVED':
                item.status = 'CLAIMED'
                item.resolved_at = now
                item.save()

                # Auto-reject any other still-PENDING ClaimAttempts on the same item
                other_pending = list(ClaimAttempt.objects.filter(item=item, status='PENDING').exclude(id=attempt.id))
                for other in other_pending:
                    other.status = 'REJECTED'
                    other.reviewed_at = now
                    other.save(update_fields=['status', 'reviewed_at'])

        serializer = ClaimAttemptSerializer(attempt, context={'request': request})
        return Response(serializer.data)


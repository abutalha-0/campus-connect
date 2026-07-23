from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.shortcuts import get_object_or_404

from classroom.access import get_user_classroom

from .models import FeedPost, FeedComment, FeedVote
from .serializers import FeedPostSerializer, FeedCommentSerializer


def require_classroom(request):
    """
    The class the requesting student belongs to (created or joined). Faculty,
    and any student not currently in a class, get 404 — Feed only exists
    inside a class.
    """
    classroom = get_user_classroom(request.user)
    if classroom is None:
        raise Http404
    return classroom


class FeedView(APIView):
    """List or create posts in the current student's class feed."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classroom = require_classroom(request)
        posts = classroom.feed_posts.prefetch_related('votes', 'comments')
        serializer = FeedPostSerializer(
            posts, many=True, context={'request': request, 'classroom': classroom}
        )
        return Response(serializer.data)

    def post(self, request):
        classroom = require_classroom(request)
        serializer = FeedPostSerializer(
            data=request.data, context={'request': request, 'classroom': classroom}
        )
        if serializer.is_valid():
            serializer.save(classroom=classroom, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedPostDetailView(APIView):
    """Edit or delete a post — its author only."""
    permission_classes = [IsAuthenticated]

    def get_post(self, request, pk):
        classroom = require_classroom(request)
        return classroom, get_object_or_404(FeedPost, id=pk, classroom=classroom)

    def patch(self, request, pk):
        classroom, post = self.get_post(request, pk)
        if post.author_id != request.user.id:
            return Response({'detail': 'You can only edit your own posts.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = FeedPostSerializer(
            post, data=request.data, partial=True,
            context={'request': request, 'classroom': classroom}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        _, post = self.get_post(request, pk)
        if post.author_id != request.user.id:
            return Response({'detail': 'You can only delete your own posts.'},
                            status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeedVoteView(APIView):
    """
    Cast a vote on a post. Sending the same value again removes the vote
    (toggle-off); sending the opposite value switches it.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        classroom = require_classroom(request)
        post = get_object_or_404(FeedPost, id=pk, classroom=classroom)

        value = request.data.get('value')
        if value not in (1, -1):
            return Response({'error': 'value must be 1 or -1.'},
                            status=status.HTTP_400_BAD_REQUEST)

        existing = FeedVote.objects.filter(post=post, user=request.user).first()
        if existing and existing.value == value:
            existing.delete()
        elif existing:
            existing.value = value
            existing.save(update_fields=['value'])
        else:
            FeedVote.objects.create(post=post, user=request.user, value=value)

        return Response(
            FeedPostSerializer(post, context={'request': request, 'classroom': classroom}).data
        )


class FeedTagOptionsView(APIView):
    """
    Subject and faculty names available to tag a post with — drawn from the
    student's own class, so the client can offer them as a picker.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classroom = require_classroom(request)
        options = set()
        for subject in classroom.subjects.select_related('faculty__user'):
            options.add(subject.name)
            options.add(subject.faculty.user.full_name)
        return Response(sorted(options))


class FeedCommentView(APIView):
    """List or add comments on a post."""
    permission_classes = [IsAuthenticated]

    def get_post(self, request, post_id):
        classroom = require_classroom(request)
        return get_object_or_404(FeedPost, id=post_id, classroom=classroom)

    def get(self, request, post_id):
        post = self.get_post(request, post_id)
        comments = post.comments.all()
        return Response(
            FeedCommentSerializer(comments, many=True, context={'request': request}).data
        )

    def post(self, request, post_id):
        post = self.get_post(request, post_id)
        serializer = FeedCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedCommentDetailView(APIView):
    """Edit or delete a comment — its author only."""
    permission_classes = [IsAuthenticated]

    def get_comment(self, request, post_id, pk):
        classroom = require_classroom(request)
        post = get_object_or_404(FeedPost, id=post_id, classroom=classroom)
        return get_object_or_404(FeedComment, id=pk, post=post)

    def patch(self, request, post_id, pk):
        comment = self.get_comment(request, post_id, pk)
        if comment.author_id != request.user.id:
            return Response({'detail': 'You can only edit your own comments.'},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = FeedCommentSerializer(
            comment, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, pk):
        comment = self.get_comment(request, post_id, pk)
        if comment.author_id != request.user.id:
            return Response({'detail': 'You can only delete your own comments.'},
                            status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

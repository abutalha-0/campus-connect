from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Bookmark, Category, JoinRequest, Post, PostMember
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    BookmarkSerializer,
    CategorySerializer,
    JoinRequestSerializer,
    PostMemberSerializer,
    PostSerializer,
)


# ─── Categories ──────────────────────────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)


# ─── Posts ───────────────────────────────────────────────────────────────────

class PostListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = Post.objects.select_related('author', 'category').prefetch_related('skills')

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.upper())

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = PostSerializer
    queryset = Post.objects.select_related('author', 'category').prefetch_related('skills')
    lookup_field = 'slug'


class PostCloseView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        self.check_object_permissions(request, post)
        services.close_post(post)
        services.cancel_stale_pending_requests(post)
        return Response(PostSerializer(post).data, status=status.HTTP_200_OK)


class PostMemberListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostMemberSerializer

    def get_queryset(self):
        return PostMember.objects.filter(post__slug=self.kwargs['slug']).select_related('user')


# ─── Join Requests ───────────────────────────────────────────────────────────

class JoinRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JoinRequestSerializer

    def get_queryset(self):
        queryset = JoinRequest.objects.select_related('post', 'requester', 'reviewed_by')

        post_slug = self.request.query_params.get('post')
        if post_slug:
            # Requests for a given post are visible to that post's author.
            return queryset.filter(post__slug=post_slug, post__author=self.request.user)

        # Otherwise, a user sees only their own outgoing requests.
        return queryset.filter(requester=self.request.user)


class JoinRequestAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        join_request = get_object_or_404(JoinRequest, pk=pk)
        if join_request.post.author_id != request.user.id:
            return Response({'error': 'Only the post owner can accept requests.'}, status=status.HTTP_403_FORBIDDEN)
        services.accept_join_request(join_request, reviewer=request.user)
        return Response(JoinRequestSerializer(join_request).data, status=status.HTTP_200_OK)


class JoinRequestRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        join_request = get_object_or_404(JoinRequest, pk=pk)
        if join_request.post.author_id != request.user.id:
            return Response({'error': 'Only the post owner can reject requests.'}, status=status.HTTP_403_FORBIDDEN)
        services.reject_join_request(join_request, reviewer=request.user)
        return Response(JoinRequestSerializer(join_request).data, status=status.HTTP_200_OK)


# ─── Bookmarks ───────────────────────────────────────────────────────────────

class BookmarkListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user).select_related('post')


class BookmarkDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

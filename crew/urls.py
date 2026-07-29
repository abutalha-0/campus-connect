from django.urls import path

from .views import (
    BookmarkDeleteView,
    BookmarkListCreateView,
    CategoryListView,
    JoinRequestAcceptView,
    JoinRequestListCreateView,
    JoinRequestRejectView,
    PostCloseView,
    PostDetailView,
    PostListCreateView,
    PostMemberListView,
)

urlpatterns = [
    # ─── Categories ──────────────────────────────────────────────────────────
    path('categories/', CategoryListView.as_view(), name='category-list'),

    # ─── Posts ───────────────────────────────────────────────────────────────
    path('posts/', PostListCreateView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<slug:slug>/close/', PostCloseView.as_view(), name='post-close'),
    path('posts/<slug:slug>/members/', PostMemberListView.as_view(), name='post-members'),

    # ─── Join Requests ───────────────────────────────────────────────────────
    path('join-requests/', JoinRequestListCreateView.as_view(), name='join-request-list'),
    path('join-requests/<int:pk>/accept/', JoinRequestAcceptView.as_view(), name='join-request-accept'),
    path('join-requests/<int:pk>/reject/', JoinRequestRejectView.as_view(), name='join-request-reject'),

    # ─── Bookmarks ───────────────────────────────────────────────────────────
    path('bookmarks/', BookmarkListCreateView.as_view(), name='bookmark-list'),
    path('bookmarks/<int:pk>/', BookmarkDeleteView.as_view(), name='bookmark-delete'),
]

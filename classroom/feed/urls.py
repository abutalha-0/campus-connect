from django.urls import path

from .views import (
    FeedView,
    FeedPostDetailView,
    FeedVoteView,
    FeedTagOptionsView,
    FeedCommentView,
    FeedCommentDetailView,
)

urlpatterns = [
    path('feed/tag-options/', FeedTagOptionsView.as_view(), name='feed-tag-options'),
    path('feed/', FeedView.as_view(), name='feed-list-create'),
    path('feed/<int:pk>/', FeedPostDetailView.as_view(), name='feed-detail'),
    path('feed/<int:pk>/vote/', FeedVoteView.as_view(), name='feed-vote'),
    path('feed/<int:post_id>/comments/', FeedCommentView.as_view(), name='feed-comment-list-create'),
    path('feed/<int:post_id>/comments/<int:pk>/', FeedCommentDetailView.as_view(), name='feed-comment-detail'),
]

from django.urls import path

from .views import NoticeView, NoticeDetailView

urlpatterns = [
    path(
        'subjects/<int:subject_id>/notices/',
        NoticeView.as_view(),
        name='notice-list-create'
    ),
    path(
        'subjects/<int:subject_id>/notices/<int:pk>/',
        NoticeDetailView.as_view(),
        name='notice-detail'
    ),
]

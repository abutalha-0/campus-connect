from django.urls import path

from .views import ResourceView, ResourceDetailView

urlpatterns = [
    path(
        'subjects/<int:subject_id>/resources/',
        ResourceView.as_view(),
        name='resource-list-create'
    ),
    path(
        'subjects/<int:subject_id>/resources/<int:pk>/',
        ResourceDetailView.as_view(),
        name='resource-detail'
    ),
]

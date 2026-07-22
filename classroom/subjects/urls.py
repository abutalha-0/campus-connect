from django.urls import path

from .views import SubjectView, SubjectDetailView

urlpatterns = [
    path('subjects/', SubjectView.as_view(), name='subject-create'),
    path('subjects/<int:pk>/', SubjectDetailView.as_view(), name='subject-detail'),
]

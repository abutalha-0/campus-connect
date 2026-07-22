from django.urls import path

from .views import (
    SubjectLookupView,
    ClassroomView,
    ClassroomMeView,
    ClassroomSubjectView,
)

urlpatterns = [
    path('classes/lookup/', SubjectLookupView.as_view(), name='class-subject-lookup'),
    path('classes/', ClassroomView.as_view(), name='class-create'),
    path('classes/me/', ClassroomMeView.as_view(), name='class-me'),
    path('classes/me/subjects/', ClassroomSubjectView.as_view(), name='class-subject-add'),
    path('classes/me/subjects/<int:subject_id>/', ClassroomSubjectView.as_view(), name='class-subject-remove'),
]

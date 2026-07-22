from django.urls import path

from .views import FacultyRegisterView

urlpatterns = [
    path('register/', FacultyRegisterView.as_view(), name='faculty-register'),
]

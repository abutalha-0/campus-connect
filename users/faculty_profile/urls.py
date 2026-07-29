from django.urls import path

from .views import (
    FacultyRegisterView,
    FacultyMeView,
    FacultyPublicProfileView,
    FacultyLinkView,
)

urlpatterns = [
    path('register/', FacultyRegisterView.as_view(), name='faculty-register'),

    # ─── Faculty Profile (own) ───────────────────────────────────────────────
    path('me/', FacultyMeView.as_view(), name='faculty-me'),

    # ─── Links ───────────────────────────────────────────────────────────────
    path('me/links/', FacultyLinkView.as_view(), name='faculty-link-create'),
    path('me/links/<int:pk>/', FacultyLinkView.as_view(), name='faculty-link-delete'),

    # ─── Faculty Profile (public) ────────────────────────────────────────────
    path('<int:user_id>/', FacultyPublicProfileView.as_view(), name='faculty-public-profile'),
]

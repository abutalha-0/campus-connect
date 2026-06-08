from django.urls import path

from .views import (
    MyProfileView,
    PublicProfileView,
    LookingForView,
    LinkView,
    EducationView,
    EducationDetailView,
    ExperienceView,
    ExperienceDetailView,
    ProjectView,
    ProjectDetailView,
    ProjectImageView,
    SkillListView,
    UserSkillView,
)

urlpatterns = [
    # ─── Profile ─────────────────────────────────────────────────────────────
    path('me/', MyProfileView.as_view(), name='my-profile'),
    path('<int:user_id>/', PublicProfileView.as_view(), name='public-profile'),

    # ─── Looking For ─────────────────────────────────────────────────────────
    path('me/looking-for/', LookingForView.as_view(), name='looking-for-create'),
    path('me/looking-for/<int:pk>/', LookingForView.as_view(), name='looking-for-delete'),

    # ─── Links ───────────────────────────────────────────────────────────────
    path('me/links/', LinkView.as_view(), name='link-create'),
    path('me/links/<int:pk>/', LinkView.as_view(), name='link-delete'),

    # ─── Education ───────────────────────────────────────────────────────────
    path('me/education/', EducationView.as_view(), name='education-create'),
    path('me/education/<int:pk>/', EducationDetailView.as_view(), name='education-detail'),

    # ─── Experience ──────────────────────────────────────────────────────────
    path('me/experience/', ExperienceView.as_view(), name='experience-create'),
    path('me/experience/<int:pk>/', ExperienceDetailView.as_view(), name='experience-detail'),

    # ─── Projects ────────────────────────────────────────────────────────────
    path('me/projects/', ProjectView.as_view(), name='project-create'),
    path('me/projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),

    # ─── Project Images ───────────────────────────────────────────────────────
    path('me/projects/<int:project_id>/images/', ProjectImageView.as_view(), name='project-image-create'),
    path('me/projects/<int:project_id>/images/<int:image_id>/', ProjectImageView.as_view(), name='project-image-delete'),

    # ─── Skills ──────────────────────────────────────────────────────────────
    path('skills/', SkillListView.as_view(), name='skill-list'),
    path('me/skills/', UserSkillView.as_view(), name='user-skill-create'),
    path('me/skills/<int:pk>/', UserSkillView.as_view(), name='user-skill-delete'),
]
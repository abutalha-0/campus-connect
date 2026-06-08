from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from shared.cloudinary_utils import upload_image

from .models import (
    Profile,
    LookingFor,
    Link,
    Education,
    Experience,
    Project,
    ProjectImage,
    Skill,
    UserSkill,
)
from .serializers import (
    PublicProfileSerializer,
    PrivateProfileSerializer,
    LookingForSerializer,
    LinkSerializer,
    EducationSerializer,
    ExperienceSerializer,
    ProjectSerializer,
    ProjectImageSerializer,
    SkillSerializer,
    UserSkillSerializer,
)

User = get_user_model()


# ─── Profile Views ────────────────────────────────────────────────────────────

class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = PrivateProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)

        data = request.data.copy()

        # handle profile photo upload if a file was sent
        if 'profile_photo' in request.FILES:
            file = request.FILES['profile_photo']
            url = upload_image(file, folder="campus_connect/profile_photos")
            data['profile_photo'] = url

        serializer = PrivateProfileSerializer(
            profile,
            data=data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id, is_active=True)
        profile = get_object_or_404(Profile, user=user)
        serializer = PublicProfileSerializer(profile)
        return Response(serializer.data)


# ─── LookingFor Views ─────────────────────────────────────────────────────────

class LookingForView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LookingForSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = get_object_or_404(LookingFor, id=pk, user=request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Link Views ───────────────────────────────────────────────────────────────

class LinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LinkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        link = get_object_or_404(Link, id=pk, user=request.user)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Education Views ──────────────────────────────────────────────────────────

class EducationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()

        if 'image' in request.FILES:
            file = request.FILES['image']
            url = upload_image(file, folder="campus_connect/education_images")
            data['image_url'] = url

        serializer = EducationSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EducationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        education = get_object_or_404(Education, id=pk, user=request.user)
        serializer = EducationSerializer(
            education,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        education = get_object_or_404(Education, id=pk, user=request.user)
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Experience Views ─────────────────────────────────────────────────────────

class ExperienceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExperienceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExperienceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        experience = get_object_or_404(Experience, id=pk, user=request.user)
        serializer = ExperienceSerializer(
            experience,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        experience = get_object_or_404(Experience, id=pk, user=request.user)
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Project Views ────────────────────────────────────────────────────────────

class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        project = get_object_or_404(Project, id=pk, user=request.user)
        serializer = ProjectSerializer(
            project,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = get_object_or_404(Project, id=pk, user=request.user)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Project Image Views ──────────────────────────────────────────────────────

class ProjectImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, user=request.user)

        data = request.data.copy()

        # handle image file upload if a file was sent
        if 'image' in request.FILES:
            file = request.FILES['image']
            url = upload_image(file, folder="campus_connect/project_images")
            data['image_url'] = url

        serializer = ProjectImageSerializer(data=data)
        if serializer.is_valid():
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id, image_id):
        project = get_object_or_404(Project, id=project_id, user=request.user)
        image = get_object_or_404(ProjectImage, id=image_id, project=project)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Skill Views ──────────────────────────────────────────────────────────────

class SkillListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('search', '')
        if query:
            skills = Skill.objects.filter(name__icontains=query)
        else:
            skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)


class UserSkillView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # check if skill name provided instead of skill_id (user creating new skill)
        skill_name = request.data.get('skill_name', '').strip()
        if skill_name:
            skill, created = Skill.objects.get_or_create(
                name__iexact=skill_name,
                defaults={'name': skill_name, 'is_predefined': False}
            )
            data = {
                'skill_id': skill.id,
                'proficiency': request.data.get('proficiency', 'BEGINNER')
            }
        else:
            data = request.data

        if UserSkill.objects.filter(user=request.user, skill_id=data.get('skill_id')).exists():
            return Response(
                {'error': 'You already have this skill.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserSkillSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_skill = get_object_or_404(UserSkill, id=pk, user=request.user)
        user_skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
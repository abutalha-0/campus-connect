from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from shared.cloudinary_utils import upload_image, delete_image, extract_public_id
from users.accounts.serializers import UserSerializer

from .models import FacultyProfile, FacultyLink
from .serializers import (
    FacultyRegisterSerializer,
    FacultyProfileSerializer,
    FacultyMeSerializer,
    FacultyLinkSerializer,
    FacultyPublicProfileSerializer,
)

User = get_user_model()


class FacultyRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FacultyRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user, faculty_profile = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'faculty_profile': FacultyProfileSerializer(faculty_profile).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Faculty Profile (own) ────────────────────────────────────────────────────

class FacultyMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(FacultyProfile, user=request.user)
        serializer = FacultyMeSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = get_object_or_404(FacultyProfile, user=request.user)
        data = request.data.copy()

        if 'profile_photo' in request.FILES:
            # delete old image from Cloudinary first
            if profile.profile_photo:
                old_public_id = extract_public_id(profile.profile_photo)
                if old_public_id:
                    delete_image(old_public_id)

            file = request.FILES['profile_photo']
            url = upload_image(file, folder="campus_connect/faculty_photos")
            data['profile_photo'] = url

        serializer = FacultyMeSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ─── Faculty Profile (public) ─────────────────────────────────────────────────

class FacultyPublicProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id, is_active=True, role='FACULTY')
        profile = get_object_or_404(FacultyProfile, user=user)
        serializer = FacultyPublicProfileSerializer(profile)
        return Response(serializer.data)


# ─── Faculty Links ────────────────────────────────────────────────────────────

class FacultyLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = get_object_or_404(FacultyProfile, user=request.user)
        serializer = FacultyLinkSerializer(data=request.data, context={'faculty': profile})
        if serializer.is_valid():
            serializer.save(faculty=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = get_object_or_404(FacultyProfile, user=request.user)
        link = get_object_or_404(FacultyLink, id=pk, faculty=profile)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

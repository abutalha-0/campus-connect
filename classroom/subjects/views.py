from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.shortcuts import get_object_or_404

from classroom.access import can_view_subject
from classroom.permissions import IsVerifiedFaculty

from .models import Subject
from .serializers import SubjectSerializer


class SubjectView(APIView):
    """
    Add a subject. Only a verified faculty account may create subjects; the
    created subject is owned by that faculty and issued a unique share code.
    """
    permission_classes = [IsAuthenticated, IsVerifiedFaculty]

    def get(self, request):
        subjects = Subject.objects.filter(faculty=request.user.faculty_profile)
        return Response(
            SubjectSerializer(subjects, many=True, context={'request': request}).data
        )

    def post(self, request):
        serializer = SubjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(faculty=request.user.faculty_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectDetailView(APIView):
    """
    Retrieve a subject (its faculty owner, or any student whose class contains
    it), or update/delete it (faculty owner only). The share `code` is
    immutable and cannot be changed through update.
    """
    permission_classes = [IsAuthenticated]

    def get_owned_subject(self, request, pk):
        faculty_profile = getattr(request.user, 'faculty_profile', None)
        if not faculty_profile or not faculty_profile.is_verified:
            raise Http404
        return get_object_or_404(Subject, id=pk, faculty=faculty_profile)

    def get(self, request, pk):
        subject = get_object_or_404(Subject, id=pk)
        if not can_view_subject(request.user, subject):
            raise Http404
        return Response(SubjectSerializer(subject, context={'request': request}).data)

    def patch(self, request, pk):
        subject = self.get_owned_subject(request, pk)
        serializer = SubjectSerializer(
            subject, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subject = self.get_owned_subject(request, pk)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

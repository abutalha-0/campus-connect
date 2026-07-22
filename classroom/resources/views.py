from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from classroom.permissions import IsVerifiedFaculty
from classroom.subjects.models import Subject
from shared.cloudinary_utils import upload_file

from .models import Resource
from .serializers import ResourceSerializer


class ResourceView(APIView):
    """
    List or add resources for a subject the requesting faculty owns. A subject
    owned by another faculty (or nonexistent) returns 404.
    """
    permission_classes = [IsAuthenticated, IsVerifiedFaculty]

    def get_subject(self, request, subject_id):
        return get_object_or_404(
            Subject, id=subject_id, faculty=request.user.faculty_profile
        )

    def get(self, request, subject_id):
        subject = self.get_subject(request, subject_id)
        resources = subject.resources.all()
        return Response(ResourceSerializer(resources, many=True).data)

    def post(self, request, subject_id):
        subject = self.get_subject(request, subject_id)
        data = request.data.copy()

        # An uploaded document takes precedence; otherwise file_url may be a
        # video link supplied directly in the body.
        if 'file' in request.FILES:
            data['file_url'] = upload_file(
                request.FILES['file'], folder="campus_connect/resources"
            )

        serializer = ResourceSerializer(data=data)
        if serializer.is_valid():
            serializer.save(subject=subject)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResourceDetailView(APIView):
    """Edit or delete a single resource within an owned subject."""
    permission_classes = [IsAuthenticated, IsVerifiedFaculty]

    def get_object(self, request, subject_id, pk):
        subject = get_object_or_404(
            Subject, id=subject_id, faculty=request.user.faculty_profile
        )
        return get_object_or_404(Resource, id=pk, subject=subject)

    def patch(self, request, subject_id, pk):
        resource = self.get_object(request, subject_id, pk)
        data = request.data.copy()

        if 'file' in request.FILES:
            data['file_url'] = upload_file(
                request.FILES['file'], folder="campus_connect/resources"
            )

        serializer = ResourceSerializer(resource, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subject_id, pk):
        resource = self.get_object(request, subject_id, pk)
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

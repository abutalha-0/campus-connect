from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.shortcuts import get_object_or_404

from classroom.access import can_view_subject, can_post_to_subject, can_modify_content
from classroom.subjects.models import Subject
from shared.cloudinary_utils import upload_file

from .models import Resource
from .serializers import ResourceSerializer


class ResourceView(APIView):
    """
    List or add resources for a subject. Viewable by the faculty owner and any
    student whose class contains the subject; postable by the faculty owner or
    the class CR.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        if not can_view_subject(request.user, subject):
            raise Http404
        resources = subject.resources.all()
        return Response(
            ResourceSerializer(resources, many=True, context={'request': request}).data
        )

    def post(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        if not can_post_to_subject(request.user, subject):
            return Response({'detail': 'You do not have permission to post resources here.'},
                            status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        if 'file' in request.FILES:
            data['file_url'] = upload_file(
                request.FILES['file'], folder="campus_connect/resources"
            )

        serializer = ResourceSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(subject=subject, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResourceDetailView(APIView):
    """Edit or delete a resource — its author, or the subject's faculty owner."""
    permission_classes = [IsAuthenticated]

    def _get(self, request, subject_id, pk):
        subject = get_object_or_404(Subject, id=subject_id)
        if not can_view_subject(request.user, subject):
            raise Http404
        resource = get_object_or_404(Resource, id=pk, subject=subject)
        return subject, resource

    def patch(self, request, subject_id, pk):
        subject, resource = self._get(request, subject_id, pk)
        if not can_modify_content(request.user, subject, resource.author_id):
            return Response({'detail': 'You can only edit your own resources.'},
                            status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        if 'file' in request.FILES:
            data['file_url'] = upload_file(
                request.FILES['file'], folder="campus_connect/resources"
            )

        serializer = ResourceSerializer(resource, data=data, partial=True,
                                        context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subject_id, pk):
        subject, resource = self._get(request, subject_id, pk)
        if not can_modify_content(request.user, subject, resource.author_id):
            return Response({'detail': 'You can only delete your own resources.'},
                            status=status.HTTP_403_FORBIDDEN)
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

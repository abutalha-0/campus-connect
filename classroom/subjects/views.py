from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

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
        return Response(SubjectSerializer(subjects, many=True).data)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(faculty=request.user.faculty_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectDetailView(APIView):
    """
    Retrieve, update, or delete a single subject. Scoped to the owning faculty:
    a subject that isn't owned by the requester returns 404. The share `code`
    is immutable and cannot be changed through update.
    """
    permission_classes = [IsAuthenticated, IsVerifiedFaculty]

    def get_object(self, request, pk):
        return get_object_or_404(
            Subject, id=pk, faculty=request.user.faculty_profile
        )

    def get(self, request, pk):
        subject = self.get_object(request, pk)
        return Response(SubjectSerializer(subject).data)

    def patch(self, request, pk):
        subject = self.get_object(request, pk)
        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subject = self.get_object(request, pk)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

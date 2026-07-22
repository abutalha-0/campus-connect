from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from classroom.permissions import IsStudent
from classroom.subjects.models import Subject
from classroom.subjects.serializers import SubjectSerializer

from .models import Classroom
from .serializers import ClassroomSerializer


class SubjectLookupView(APIView):
    """Resolve a subject secret code to its details (for the 'add course' draft)."""
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        code = request.query_params.get('code', '').strip()
        if not code:
            return Response({'error': 'A code is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        subject = Subject.objects.filter(code=code).first()
        if not subject:
            return Response({'error': 'No subject found with that code.'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(SubjectSerializer(subject).data)


class ClassroomView(APIView):
    """Create the current student's class (one per user)."""
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        if hasattr(request.user, 'owned_class'):
            return Response(
                {'error': 'You already have a class. Delete it before creating a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        classroom = Classroom.objects.create(
            creator=request.user,
            code=Classroom.generate_unique_code()
        )

        # Optionally seed with subjects by their secret codes (client has already
        # validated these via the lookup endpoint). Unknown codes are ignored.
        codes = request.data.get('subject_codes')
        if isinstance(codes, list) and codes:
            classroom.subjects.set(Subject.objects.filter(code__in=codes))

        return Response(ClassroomSerializer(classroom).data,
                        status=status.HTTP_201_CREATED)


class ClassroomMeView(APIView):
    """Retrieve or delete the current student's class."""
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        classroom = get_object_or_404(Classroom, creator=request.user)
        return Response(ClassroomSerializer(classroom).data)

    def delete(self, request):
        classroom = get_object_or_404(Classroom, creator=request.user)
        password = request.data.get('password', '')
        if not request.user.check_password(password):
            return Response({'error': 'Incorrect password.'},
                            status=status.HTTP_400_BAD_REQUEST)
        classroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassroomSubjectView(APIView):
    """Add or remove a course (subject) in the current student's class."""
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        classroom = get_object_or_404(Classroom, creator=request.user)
        code = (request.data.get('code') or '').strip()
        subject = Subject.objects.filter(code=code).first()
        if not subject:
            return Response({'error': 'No subject found with that code.'},
                            status=status.HTTP_404_NOT_FOUND)
        if classroom.subjects.filter(id=subject.id).exists():
            return Response({'error': 'This course is already in your class.'},
                            status=status.HTTP_400_BAD_REQUEST)
        classroom.subjects.add(subject)
        return Response(SubjectSerializer(subject).data,
                        status=status.HTTP_201_CREATED)

    def delete(self, request, subject_id):
        classroom = get_object_or_404(Classroom, creator=request.user)
        subject = get_object_or_404(Subject, id=subject_id)
        classroom.subjects.remove(subject)
        return Response(status=status.HTTP_204_NO_CONTENT)

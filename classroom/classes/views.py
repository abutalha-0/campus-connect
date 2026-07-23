from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from classroom.permissions import IsStudent
from classroom.subjects.models import Subject
from classroom.subjects.serializers import SubjectSerializer

from .models import Classroom, ClassMembership
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
        # Only a CR may create a class.
        student_profile = getattr(request.user, 'student_profile', None)
        if not student_profile or student_profile.user_type != 'CR':
            return Response(
                {'error': 'Only a CR can create a class. Configure it from your profile.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if hasattr(request.user, 'owned_class'):
            return Response(
                {'error': 'You already have a class. Delete it before creating a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if hasattr(request.user, 'class_membership'):
            return Response(
                {'error': 'You are already in a class. Leave it before creating your own.'},
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

        return Response(ClassroomSerializer(classroom, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)


class ClassroomMeView(APIView):
    """
    Retrieve the current student's class (created OR joined), or delete it
    (creators only — members leave via the leave endpoint).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        classroom = _resolve_class(request.user)
        if classroom is None:
            return Response({'detail': 'You are not in a class.'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response(ClassroomSerializer(classroom, context={'request': request}).data)

    def delete(self, request):
        classroom = get_object_or_404(Classroom, creator=request.user)
        password = request.data.get('password', '')
        if not request.user.check_password(password):
            return Response({'error': 'Incorrect password.'},
                            status=status.HTTP_400_BAD_REQUEST)
        classroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def _resolve_class(user):
    """The class a student belongs to: the one they created, else the one they joined."""
    owned = getattr(user, 'owned_class', None)
    if owned is not None:
        return owned
    membership = getattr(user, 'class_membership', None)
    return membership.classroom if membership is not None else None


class JoinClassView(APIView):
    """Join a class by its code."""
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        if hasattr(request.user, 'owned_class'):
            return Response(
                {'error': 'You already have your own class. Delete it before joining another.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if hasattr(request.user, 'class_membership'):
            return Response(
                {'error': 'You are already in a class. Leave it before joining another.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        code = (request.data.get('code') or '').strip()
        classroom = Classroom.objects.filter(code__iexact=code).first()
        if not classroom:
            return Response({'error': 'No class found with that code.'},
                            status=status.HTTP_404_NOT_FOUND)

        ClassMembership.objects.create(classroom=classroom, student=request.user)
        return Response(ClassroomSerializer(classroom, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)


class LeaveClassView(APIView):
    """Leave the class the student has joined."""
    permission_classes = [IsAuthenticated, IsStudent]

    def delete(self, request):
        membership = getattr(request.user, 'class_membership', None)
        if membership is None:
            return Response({'error': 'You are not a member of any class.'},
                            status=status.HTTP_400_BAD_REQUEST)
        membership.delete()
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

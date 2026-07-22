from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from classroom.permissions import IsVerifiedFaculty
from classroom.subjects.models import Subject
from shared.cloudinary_utils import upload_file

from .models import Notice
from .serializers import NoticeSerializer


class NoticeView(APIView):
    """
    List or post notices for a subject the requesting faculty owns. (CRs will
    be able to post once the class/enrollment feature exists; for now only the
    owning faculty may.)
    """
    permission_classes = [IsAuthenticated, IsVerifiedFaculty]

    def get_subject(self, request, subject_id):
        return get_object_or_404(
            Subject, id=subject_id, faculty=request.user.faculty_profile
        )

    def get(self, request, subject_id):
        subject = self.get_subject(request, subject_id)
        notices = subject.notices.all()
        serializer = NoticeSerializer(notices, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, subject_id):
        subject = self.get_subject(request, subject_id)

        save_kwargs = {'subject': subject, 'author': request.user}
        if 'file' in request.FILES:
            save_kwargs['attachment_url'] = upload_file(
                request.FILES['file'], folder="campus_connect/notice_attachments"
            )

        serializer = NoticeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(**save_kwargs)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoticeDetailView(APIView):
    """Edit or delete a single notice. Only the notice's author may do so."""
    permission_classes = [IsAuthenticated, IsVerifiedFaculty]

    def get_object(self, request, subject_id, pk):
        subject = get_object_or_404(
            Subject, id=subject_id, faculty=request.user.faculty_profile
        )
        return get_object_or_404(Notice, id=pk, subject=subject)

    def patch(self, request, subject_id, pk):
        notice = self.get_object(request, subject_id, pk)
        if notice.author_id != request.user.id:
            return Response(
                {'detail': 'You can only edit your own notices.'},
                status=status.HTTP_403_FORBIDDEN
            )

        save_kwargs = {}
        if 'file' in request.FILES:
            save_kwargs['attachment_url'] = upload_file(
                request.FILES['file'], folder="campus_connect/notice_attachments"
            )

        serializer = NoticeSerializer(
            notice, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(**save_kwargs)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subject_id, pk):
        notice = self.get_object(request, subject_id, pk)
        if notice.author_id != request.user.id:
            return Response(
                {'detail': 'You can only delete your own notices.'},
                status=status.HTTP_403_FORBIDDEN
            )
        notice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

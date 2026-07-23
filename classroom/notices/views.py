from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.shortcuts import get_object_or_404

from classroom.access import can_view_subject, can_post_to_subject, can_modify_content
from classroom.subjects.models import Subject
from shared.cloudinary_utils import upload_file

from .models import Notice
from .serializers import NoticeSerializer


class NoticeView(APIView):
    """
    List or post notices for a subject. Viewable by the faculty owner and any
    student whose class contains the subject; postable by the faculty owner or
    the class CR.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        if not can_view_subject(request.user, subject):
            raise Http404
        notices = subject.notices.all()
        return Response(
            NoticeSerializer(notices, many=True, context={'request': request}).data
        )

    def post(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        if not can_post_to_subject(request.user, subject):
            return Response({'detail': 'You do not have permission to post notices here.'},
                            status=status.HTTP_403_FORBIDDEN)

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
    """Edit or delete a notice — its author, or the subject's faculty owner."""
    permission_classes = [IsAuthenticated]

    def _get(self, request, subject_id, pk):
        subject = get_object_or_404(Subject, id=subject_id)
        if not can_view_subject(request.user, subject):
            raise Http404
        notice = get_object_or_404(Notice, id=pk, subject=subject)
        return subject, notice

    def patch(self, request, subject_id, pk):
        subject, notice = self._get(request, subject_id, pk)
        if not can_modify_content(request.user, subject, notice.author_id):
            return Response({'detail': 'You can only edit your own notices.'},
                            status=status.HTTP_403_FORBIDDEN)

        save_kwargs = {}
        if 'file' in request.FILES:
            save_kwargs['attachment_url'] = upload_file(
                request.FILES['file'], folder="campus_connect/notice_attachments"
            )

        serializer = NoticeSerializer(notice, data=request.data, partial=True,
                                      context={'request': request})
        if serializer.is_valid():
            serializer.save(**save_kwargs)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subject_id, pk):
        subject, notice = self._get(request, subject_id, pk)
        if not can_modify_content(request.user, subject, notice.author_id):
            return Response({'detail': 'You can only delete your own notices.'},
                            status=status.HTTP_403_FORBIDDEN)
        notice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

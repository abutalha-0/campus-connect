from datetime import date, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import Http404

from classroom.access import get_user_classroom
from classroom.notices.models import Notice

from .serializers import ScheduleEventSerializer


def start_of_week(d):
    """The Saturday that starts d's Saturday–Friday week (same convention
    the app already uses to group Resources by week)."""
    days_since_saturday = (d.weekday() - 5) % 7  # Mon=0 … Sun=6; Saturday=5
    return d - timedelta(days=days_since_saturday)


class ScheduleView(APIView):
    """
    Auto-collected schedule: every dated notice (event_date set) across every
    subject in the student's class, from the current week onward. Only class
    members (student or CR) can see it — faculty, and students not in a
    class, get 404.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classroom = get_user_classroom(request.user)
        if classroom is None:
            raise Http404

        cutoff = start_of_week(date.today())
        notices = (
            Notice.objects
            .filter(subject__in=classroom.subjects.all(), event_date__gte=cutoff)
            .select_related('subject', 'author')
            .order_by('event_date', 'event_time')
        )
        return Response(ScheduleEventSerializer(notices, many=True).data)

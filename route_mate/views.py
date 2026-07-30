from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Route, RouteJoinRequest
from .serializers import RouteSerializer, RouteJoinRequestSerializer


class RouteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        routes = Route.objects.all()
        home_area = request.query_params.get('home_area')
        destination = request.query_params.get('destination')
        gender_preference = request.query_params.get('gender_preference')
        days = request.query_params.get('days')
        status_filter = request.query_params.get('status')
        search = request.query_params.get('search')

        if home_area:
            routes = routes.filter(home_area__icontains=home_area)

        if destination:
            routes = routes.filter(destination__icontains=destination)

        if gender_preference:
            routes = routes.filter(gender_preference=gender_preference.upper())

        if days:
            routes = routes.filter(days_active__icontains=days)

        if status_filter:
            routes = routes.filter(status=status_filter.upper())
        else:
            # By default, browse view shows ACTIVE routes
            routes = routes.filter(status='ACTIVE')

        if search:
            routes = routes.filter(
                Q(home_area__icontains=search) |
                Q(destination__icontains=search) |
                Q(transport_mode__icontains=search) |
                Q(note__icontains=search)
            )

        return routes

    def get(self, request):
        routes = self.get_queryset(request)
        serializer = RouteSerializer(routes, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = RouteSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        route = get_object_or_404(Route, id=pk)
        serializer = RouteSerializer(route, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        route = get_object_or_404(Route, id=pk)
        if route.owner != request.user and not request.user.is_staff:
            return Response({'detail': 'You can only edit your own route.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RouteSerializer(route, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        route = get_object_or_404(Route, id=pk)
        if route.owner != request.user and not request.user.is_staff:
            return Response({'detail': 'You can only delete your own route.'}, status=status.HTTP_403_FORBIDDEN)
        route.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RouteJoinRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        route = get_object_or_404(Route, id=pk)

        if route.owner == request.user:
            return Response({'detail': 'You cannot request to join your own route.'}, status=status.HTTP_400_BAD_REQUEST)

        if route.status != 'ACTIVE':
            return Response({'detail': 'This route is currently not accepting join requests.'}, status=status.HTTP_400_BAD_REQUEST)

        existing = RouteJoinRequest.objects.filter(route=route, requester=request.user).first()
        if existing:
            if existing.status in ('PENDING', 'ACCEPTED'):
                return Response(
                    {'detail': f'You already have a request for this route with status "{existing.status}".'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Re-open rejected or cancelled request
                existing.status = 'PENDING'
                existing.note = request.data.get('note', existing.note)
                existing.requester_contact_info = request.data.get('requester_contact_info', existing.requester_contact_info)
                existing.save()
                serializer = RouteJoinRequestSerializer(existing, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = RouteJoinRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(route=route, requester=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteJoinRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        route = get_object_or_404(Route, id=pk)
        if route.owner != request.user and not request.user.is_staff:
            return Response({'detail': 'Only the route owner can view join requests.'}, status=status.HTTP_403_FORBIDDEN)

        requests = route.join_requests.all()
        serializer = RouteJoinRequestSerializer(requests, many=True, context={'request': request})
        return Response(serializer.data)


class RouteJoinRequestRespondView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        join_request = get_object_or_404(RouteJoinRequest, id=pk)
        if join_request.route.owner != request.user and not request.user.is_staff:
            return Response({'detail': 'Only the route owner can respond to join requests.'}, status=status.HTTP_403_FORBIDDEN)

        action = request.data.get('action') or request.data.get('status')
        if not action:
            return Response({'detail': 'Action (ACCEPT or REJECT) is required.'}, status=status.HTTP_400_BAD_REQUEST)

        action_upper = action.upper()
        if action_upper in ('ACCEPT', 'ACCEPTED'):
            join_request.status = 'ACCEPTED'
        elif action_upper in ('REJECT', 'REJECTED'):
            join_request.status = 'REJECTED'
        else:
            return Response({'detail': 'Invalid action. Choose ACCEPT or REJECT.'}, status=status.HTTP_400_BAD_REQUEST)

        join_request.save()
        serializer = RouteJoinRequestSerializer(join_request, context={'request': request})
        return Response(serializer.data)


class MyRoutesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posted_routes = Route.objects.filter(owner=request.user)
        joined_requests = RouteJoinRequest.objects.filter(requester=request.user)

        posted_serializer = RouteSerializer(posted_routes, many=True, context={'request': request})
        joined_serializer = RouteJoinRequestSerializer(joined_requests, many=True, context={'request': request})

        return Response({
            'posted_routes': posted_serializer.data,
            'joined_routes': joined_serializer.data
        })


class RouteHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Past matches / closed routes posted by user or accepted join requests
        past_posted = Route.objects.filter(owner=request.user, status='CLOSED')
        accepted_matches = RouteJoinRequest.objects.filter(
            Q(requester=request.user) | Q(route__owner=request.user),
            status='ACCEPTED'
        ).distinct()

        past_posted_serializer = RouteSerializer(past_posted, many=True, context={'request': request})
        accepted_serializer = RouteJoinRequestSerializer(accepted_matches, many=True, context={'request': request})

        return Response({
            'closed_posted_routes': past_posted_serializer.data,
            'accepted_matches': accepted_serializer.data
        })

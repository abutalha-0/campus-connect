from django.urls import path
from .views import (
    RouteListView,
    RouteDetailView,
    RouteJoinRequestCreateView,
    RouteJoinRequestListView,
    RouteJoinRequestRespondView,
    MyRoutesView,
    RouteHistoryView
)

urlpatterns = [
    path('routes/', RouteListView.as_view(), name='route-list'),
    path('routes/<int:pk>/', RouteDetailView.as_view(), name='route-detail'),
    path('routes/<int:pk>/request/', RouteJoinRequestCreateView.as_view(), name='route-join-request-create'),
    path('routes/<int:pk>/requests/', RouteJoinRequestListView.as_view(), name='route-join-request-list'),
    path('requests/<int:pk>/respond/', RouteJoinRequestRespondView.as_view(), name='route-request-respond'),
    path('my-routes/', MyRoutesView.as_view(), name='my-routes'),
    path('history/', RouteHistoryView.as_view(), name='route-history'),
]

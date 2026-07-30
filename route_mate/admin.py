from django.contrib import admin
from .models import Route, RouteJoinRequest


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'home_area', 'destination', 'gender_preference', 'status', 'created_at')
    list_filter = ('gender_preference', 'status', 'created_at')
    search_fields = ('home_area', 'destination', 'owner__username', 'owner__email')


@admin.register(RouteJoinRequest)
class RouteJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'route', 'requester', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('requester__username', 'route__home_area', 'route__destination')

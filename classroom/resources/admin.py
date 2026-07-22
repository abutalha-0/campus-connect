from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'topic', 'resource_type', 'created_at')
    list_filter = ('resource_type',)
    search_fields = ('title', 'topic', 'subject__name')
    readonly_fields = ('created_at',)

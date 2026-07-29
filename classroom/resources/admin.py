from django.contrib import admin
from django.utils.html import format_html

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'resource_type', 'author', 'file_link', 'created_at')
    list_filter = ('resource_type',)
    search_fields = ('title', 'subject__name', 'author__full_name')
    readonly_fields = ('created_at', 'file_link')
    autocomplete_fields = ['subject', 'author']
    date_hierarchy = 'created_at'

    @admin.display(description='File')
    def file_link(self, obj):
        if not obj.file_url:
            return "—"
        return format_html('<a href="{}" target="_blank">Open ↗</a>', obj.file_url)

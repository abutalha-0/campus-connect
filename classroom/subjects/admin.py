from django.contrib import admin

from classroom.notices.models import Notice

from .models import Subject


class NoticeInline(admin.TabularInline):
    """Quick glance at a subject's notices — full moderation stays on the
    Notices admin, which has richer filters (author, has-a-date, etc.)."""
    model = Notice
    fields = ('title', 'author', 'event_date', 'created_at')
    readonly_fields = fields
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'intake', 'section', 'room', 'faculty',
        'resource_count', 'notice_count', 'created_at',
    )
    list_filter = ('intake', 'section')
    search_fields = ('name', 'code', 'faculty__user__full_name')
    readonly_fields = ('code', 'created_at')
    autocomplete_fields = ['faculty']
    date_hierarchy = 'created_at'
    inlines = [NoticeInline]

    @admin.display(description='Resources')
    def resource_count(self, obj):
        return obj.resources.count()

    @admin.display(description='Notices')
    def notice_count(self, obj):
        return obj.notices.count()

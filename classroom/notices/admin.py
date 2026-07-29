from django.contrib import admin

from .models import Notice


class HasScheduledDateFilter(admin.SimpleListFilter):
    """Quickly separate notices that show up on Schedule from plain announcements."""
    title = 'scheduled date'
    parameter_name = 'has_date'

    def lookups(self, request, model_admin):
        return (('yes', 'Has a date'), ('no', 'No date'))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(event_date__isnull=False)
        if self.value() == 'no':
            return queryset.filter(event_date__isnull=True)
        return queryset


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'author', 'highlight', 'event_date', 'event_time', 'created_at')
    list_filter = (HasScheduledDateFilter, 'subject')
    search_fields = ('title', 'text', 'highlight', 'subject__name', 'author__full_name')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['subject', 'author']
    date_hierarchy = 'created_at'

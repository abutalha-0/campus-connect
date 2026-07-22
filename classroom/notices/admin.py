from django.contrib import admin

from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('subject', 'author', 'short_text', 'created_at')
    search_fields = ('text', 'subject__name', 'author__full_name')
    readonly_fields = ('created_at',)

    @admin.display(description='Text')
    def short_text(self, obj):
        return (obj.text[:60] + '…') if len(obj.text) > 60 else obj.text

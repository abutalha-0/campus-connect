from django.contrib import admin

from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'intake', 'section', 'room', 'faculty', 'created_at')
    list_filter = ('intake', 'section')
    search_fields = ('name', 'code', 'faculty__user__full_name')
    readonly_fields = ('code', 'created_at')

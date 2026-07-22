from django.contrib import admin

from .models import Classroom


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('code', 'creator', 'created_at')
    search_fields = ('code', 'creator__username', 'creator__full_name')
    filter_horizontal = ('subjects',)
    readonly_fields = ('code', 'created_at')

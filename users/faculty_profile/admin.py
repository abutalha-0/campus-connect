from django.contrib import admin

from .models import FacultyProfile, FacultyLink


class FacultyLinkInline(admin.TabularInline):
    model = FacultyLink
    extra = 0


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'designation', 'is_verified')
    list_filter = ('is_verified', 'designation', 'department')
    search_fields = ('user__full_name', 'user__email', 'employee_id')
    list_editable = ('is_verified',)
    inlines = [FacultyLinkInline]

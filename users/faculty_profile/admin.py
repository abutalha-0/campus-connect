from django.contrib import admin

from shared.admin_utils import thumbnail
from classroom.subjects.models import Subject

from .models import FacultyProfile, FacultyLink


class FacultyLinkInline(admin.TabularInline):
    model = FacultyLink
    extra = 1


class SubjectsTaughtInline(admin.TabularInline):
    """Read-only glance at what this faculty teaches — subjects themselves
    are managed via the Subjects admin, not created here."""
    model = Subject
    fields = ('name', 'code', 'intake', 'section', 'room', 'created_at')
    readonly_fields = ('name', 'code', 'intake', 'section', 'room', 'created_at')
    extra = 0
    can_delete = False
    verbose_name_plural = "Subjects taught (read-only — manage in Subjects)"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo_preview', 'employee_id', 'department', 'designation', 'is_verified')
    list_filter = ('is_verified', 'designation', 'department')
    search_fields = ('user__full_name', 'user__email', 'employee_id')
    list_editable = ('is_verified',)
    readonly_fields = ('updated_at', 'photo_preview')
    autocomplete_fields = ['user']
    # FacultyProfile has no model-level ordering; needed so paginated
    # results (e.g. the Subject.faculty autocomplete) are stable.
    ordering = ('user__full_name',)
    inlines = [FacultyLinkInline, SubjectsTaughtInline]
    actions = ['mark_verified', 'mark_unverified']

    @admin.display(description='Photo')
    def photo_preview(self, obj):
        return thumbnail(obj.profile_photo)

    @admin.action(description="Mark selected as verified")
    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} faculty profile(s) verified.")

    @admin.action(description="Mark selected as unverified")
    def mark_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} faculty profile(s) marked unverified.")

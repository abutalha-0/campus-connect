from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.student_profile.models import (
    Profile,
    LookingFor,
    Link,
    Education,
    Experience,
    Project,
    UserSkill,
)
from users.faculty_profile.models import FacultyProfile

from .models import User


# ─── Student-side inlines (shown only for role == STUDENT) ────────────────────
# These models FK straight to User (not to Profile), so they inline here
# rather than on ProfileAdmin — this turns a user's admin page into a full
# 360° view: bio, education, experience, projects, skills, links, all in
# one place instead of hunting across separate model lists.

class StudentProfileInline(admin.StackedInline):
    model = Profile
    extra = 1
    max_num = 1
    verbose_name_plural = "Student profile (bio, about, dob, gender, photo)"


class LookingForInline(admin.TabularInline):
    model = LookingFor
    extra = 1


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 1
    show_change_link = True  # projects have their own images inline — jump there to manage those


class UserSkillInline(admin.TabularInline):
    model = UserSkill
    extra = 1
    autocomplete_fields = ['skill']


# ─── Faculty-side inline (shown only for role == FACULTY) ─────────────────────

class FacultyProfileInline(admin.StackedInline):
    model = FacultyProfile
    extra = 1
    max_num = 1
    verbose_name_plural = "Faculty profile (employee ID, department, designation, verification)"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'full_name', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'full_name')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    actions = ['activate_users', 'deactivate_users']

    fieldsets = (
        ('Login info', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'full_name', 'bio')}),
        # role is read-only: nothing in the app supports changing a user's
        # role after registration, and doing it here would silently orphan
        # their student/faculty profile (each is only ever created at
        # registration time, not kept in sync with later role edits).
        ('Account type', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'created_at')}),
    )
    readonly_fields = ('role', 'created_at')

    # role is deliberately absent here — new users created via this form
    # always default to STUDENT (the model default). Creating a FACULTY user
    # requires a paired FacultyProfile (employee ID, department, etc.), which
    # only the app's own /api/faculty/register/ flow sets up atomically; a
    # bare admin-created FACULTY user would break on first faculty-only
    # request. Use the app's registration flow for faculty accounts.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'full_name', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    def get_inline_instances(self, request, obj=None):
        # No inlines on the "add user" page — profiles are created through
        # the app's own registration flows, not assembled by hand here.
        if obj is None:
            return []
        if obj.role == 'FACULTY':
            inline_classes = [FacultyProfileInline]
        else:
            inline_classes = [
                StudentProfileInline, EducationInline, ExperienceInline,
                ProjectInline, UserSkillInline, LinkInline, LookingForInline,
            ]
        return [cls(self.model, self.admin_site) for cls in inline_classes]

    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) activated.")

    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) deactivated.")

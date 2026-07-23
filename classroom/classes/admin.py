from django.contrib import admin

from .models import Classroom, ClassMembership


class ClassMembershipInline(admin.TabularInline):
    """Who's in this class — editable here for support/moderation (e.g.
    manually removing a problem member) without leaving the class's page."""
    model = ClassMembership
    extra = 0
    readonly_fields = ('joined_at',)
    autocomplete_fields = ['student']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('code', 'creator', 'subject_count', 'member_count', 'created_at')
    search_fields = ('code', 'creator__username', 'creator__full_name')
    autocomplete_fields = ['creator', 'subjects']
    readonly_fields = ('code', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [ClassMembershipInline]

    @admin.display(description='Subjects')
    def subject_count(self, obj):
        return obj.subjects.count()

    @admin.display(description='Members')
    def member_count(self, obj):
        return obj.memberships.count()


@admin.register(ClassMembership)
class ClassMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'joined_at')
    search_fields = ('student__username', 'student__full_name', 'classroom__code')
    readonly_fields = ('joined_at',)
    autocomplete_fields = ['student', 'classroom']
    ordering = ('-joined_at',)
    date_hierarchy = 'joined_at'

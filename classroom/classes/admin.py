from django.contrib import admin

from .models import Classroom, ClassMembership


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('code', 'creator', 'created_at')
    search_fields = ('code', 'creator__username', 'creator__full_name')
    filter_horizontal = ('subjects',)
    readonly_fields = ('code', 'created_at')


@admin.register(ClassMembership)
class ClassMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'joined_at')
    search_fields = ('student__username', 'student__full_name', 'classroom__code')
    readonly_fields = ('joined_at',)

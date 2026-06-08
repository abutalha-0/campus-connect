from django.contrib import admin

from .models import (
    Profile,
    LookingFor,
    Link,
    Education,
    Experience,
    Project,
    ProjectImage,
    Skill,
    UserSkill,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'updated_at')
    list_filter = ('user_type', 'gender')
    search_fields = ('user__username', 'user__email', 'user__full_name')
    readonly_fields = ('updated_at',)


@admin.register(LookingFor)
class LookingForAdmin(admin.ModelAdmin):
    list_display = ('user', 'value')
    search_fields = ('user__username', 'value')


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'link_name', 'url')
    search_fields = ('user__username', 'link_name')


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution_name', 'degree', 'start_year', 'end_year')
    search_fields = ('user__username', 'institution_name', 'degree')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'organization', 'start_date', 'end_date')
    search_fields = ('user__username', 'title', 'organization')


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    readonly_fields = ('uploaded_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'associated_with', 'created_at')
    search_fields = ('user__username', 'name')
    inlines = [ProjectImageInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_predefined')
    list_filter = ('is_predefined',)
    search_fields = ('name',)


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'proficiency')
    list_filter = ('proficiency',)
    search_fields = ('user__username', 'skill__name')
from django.contrib import admin

from shared.admin_utils import thumbnail

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
    list_display = ('user', 'photo_preview', 'user_type', 'updated_at')
    list_filter = ('user_type', 'gender')
    search_fields = ('user__username', 'user__email', 'user__full_name')
    readonly_fields = ('updated_at', 'photo_preview')
    autocomplete_fields = ['user']

    @admin.display(description='Photo')
    def photo_preview(self, obj):
        return thumbnail(obj.profile_photo)


@admin.register(LookingFor)
class LookingForAdmin(admin.ModelAdmin):
    list_display = ('user', 'value')
    search_fields = ('user__username', 'value')
    autocomplete_fields = ['user']


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'link_name', 'url')
    search_fields = ('user__username', 'link_name')
    autocomplete_fields = ['user']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('user', 'logo_preview', 'institution_name', 'degree', 'start_year', 'end_year')
    search_fields = ('user__username', 'institution_name', 'degree')
    readonly_fields = ('logo_preview',)
    autocomplete_fields = ['user']

    @admin.display(description='Logo')
    def logo_preview(self, obj):
        return thumbnail(obj.image_url)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'organization', 'start_date', 'end_date')
    search_fields = ('user__username', 'title', 'organization')
    autocomplete_fields = ['user']


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    readonly_fields = ('uploaded_at', 'thumb')

    @admin.display(description='Preview')
    def thumb(self, obj):
        return thumbnail(obj.image_url)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'associated_with', 'created_at')
    search_fields = ('user__username', 'name')
    autocomplete_fields = ['user']
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
    autocomplete_fields = ['user', 'skill']

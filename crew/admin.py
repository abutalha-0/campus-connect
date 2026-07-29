from django.contrib import admin

from .models import Bookmark, Category, JoinRequest, Post, PostMember


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'max_members', 'created_at')
    list_filter = ('status', 'category', 'is_featured')
    search_fields = ('title', 'author__username', 'author__email', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'post', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('requester__username', 'post__title')


@admin.register(PostMember)
class PostMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'joined_at')
    search_fields = ('user__username', 'post__title')


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')

from django.contrib import admin

from .models import FeedPost, FeedVote, FeedComment


class FeedCommentInline(admin.TabularInline):
    model = FeedComment
    extra = 0


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'classroom', 'author', 'tag', 'created_at')
    search_fields = ('title', 'body', 'author__full_name', 'classroom__code')
    inlines = [FeedCommentInline]


@admin.register(FeedVote)
class FeedVoteAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'value')


@admin.register(FeedComment)
class FeedCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')

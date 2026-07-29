from django.contrib import admin
from django.db.models import Sum

from .models import FeedPost, FeedVote, FeedComment


class FeedCommentInline(admin.TabularInline):
    model = FeedComment
    extra = 0
    readonly_fields = ('created_at',)
    autocomplete_fields = ['author']


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'classroom', 'author', 'tag', 'score', 'comment_count', 'created_at')
    list_filter = ('classroom',)
    search_fields = ('title', 'body', 'author__full_name', 'classroom__code')
    autocomplete_fields = ['classroom', 'author']
    date_hierarchy = 'created_at'
    inlines = [FeedCommentInline]

    @admin.display(description='Score')
    def score(self, obj):
        return obj.votes.aggregate(total=Sum('value'))['total'] or 0

    @admin.display(description='Comments')
    def comment_count(self, obj):
        return obj.comments.count()


@admin.register(FeedVote)
class FeedVoteAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'value')
    list_filter = ('value',)
    autocomplete_fields = ['post', 'user']


@admin.register(FeedComment)
class FeedCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    search_fields = ('text', 'author__full_name', 'post__title')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['post', 'author']
    date_hierarchy = 'created_at'

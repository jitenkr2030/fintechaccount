"""Admin for the networking app."""
from django.contrib import admin

from .models import Connection, Post, Comment, Like


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'kind', 'status', 'created_at')
    list_filter = ('kind', 'status')
    search_fields = ('from_user__email', 'to_user__email')


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'body', 'created_at')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'post_type', 'title', 'likes_count',
                    'comments_count', 'is_pinned', 'is_flagged', 'created_at')
    list_filter = ('post_type', 'is_pinned', 'is_flagged')
    search_fields = ('title', 'body', 'author__email')
    readonly_fields = ('likes_count', 'comments_count', 'shares_count')
    inlines = [CommentInline]


admin.site.register(Comment)
admin.site.register(Like)

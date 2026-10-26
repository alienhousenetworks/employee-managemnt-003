from django.contrib import admin
from .models import FeedPost, FeedComment, FeedReaction


@admin.register(FeedPost)
class FeedPostAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "author", "post_type", "visibility", "created_at")
    list_filter = ("organization", "post_type", "visibility", "created_at")
    search_fields = ("body", "author__username", "linked_record_id")
    readonly_fields = ("id", "created_at", "updated_at")
    autocomplete_fields = ("organization", "author")


@admin.register(FeedComment)
class FeedCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
    search_fields = ("body", "author__username")
    readonly_fields = ("created_at",)


@admin.register(FeedReaction)
class FeedReactionAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "reaction", "created_at")
    list_filter = ("reaction", "created_at")
    readonly_fields = ("created_at",)

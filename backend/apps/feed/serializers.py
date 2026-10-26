from rest_framework import serializers
from .models import FeedPost, FeedComment, FeedReaction

class FeedCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_username", read_only=True)
    class Meta:
        model = FeedComment
        fields = ["id", "author", "author_name", "body", "created_at"]
        read_only_fields = ["id", "author", "author_name", "created_at"]

class FeedPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_username", read_only=True)
    comments = FeedCommentSerializer(many=True, read_only=True)
    reaction_count = serializers.IntegerField(source="reactions.count", read_only=True)
    class Meta:
        model = FeedPost
        fields = ["id", "author", "author_name", "post_type", "visibility", "department", "body", "linked_record_type", "linked_record_id", "comments", "reaction_count", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "author_name", "comments", "reaction_count", "created_at", "updated_at"]

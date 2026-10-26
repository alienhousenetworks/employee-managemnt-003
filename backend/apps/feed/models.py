import uuid
from django.conf import settings
from django.db import models
from apps.organizations.models import Organization

class FeedPost(models.Model):
    class PostType(models.TextChoices):
        GENERAL_UPDATE = "GENERAL_UPDATE", "General update"
        PROGRESS = "PROGRESS", "Progress"
        EOD_REPORT = "EOD_REPORT", "EOD report"
        HELP_REQUEST = "HELP_REQUEST", "Help request"
        KNOWLEDGE_SHARE = "KNOWLEDGE_SHARE", "Knowledge share"
        QUESTION = "QUESTION", "Question"
        ANNOUNCEMENT = "ANNOUNCEMENT", "Announcement"
        BLOCKER = "BLOCKER", "Blocker"
        PROJECT_UPDATE = "PROJECT_UPDATE", "Project update"
        AI_INSIGHT = "AI_INSIGHT", "AI insight"
        RECOGNITION = "RECOGNITION", "Recognition"
    class Visibility(models.TextChoices):
        ORGANIZATION = "ORGANIZATION", "Organization"
        DEPARTMENT = "DEPARTMENT", "Department"
        PROJECT = "PROJECT", "Project"
        PRIVATE = "PRIVATE", "Author only"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="feed_posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feed_posts")
    post_type = models.CharField(max_length=24, choices=PostType.choices, default=PostType.GENERAL_UPDATE)
    visibility = models.CharField(max_length=16, choices=Visibility.choices, default=Visibility.ORGANIZATION)
    department = models.CharField(max_length=100, blank=True)
    body = models.TextField(max_length=10000)
    linked_record_type = models.CharField(max_length=60, blank=True)
    linked_record_id = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "visibility", "created_at"])]

class FeedComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(FeedPost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

class FeedReaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(FeedPost, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=24, default="LIKE")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["post", "user", "reaction"], name="uniq_feed_reaction")]

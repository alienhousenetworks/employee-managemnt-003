import uuid
from django.conf import settings
from django.db import models
from apps.organizations.models import Organization

class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="audit_events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=120)
    object_type = models.CharField(max_length=80)
    object_id = models.CharField(max_length=100, blank=True)
    request_id = models.CharField(max_length=100, blank=True, db_index=True)
    outcome = models.CharField(max_length=24, default="SUCCESS")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

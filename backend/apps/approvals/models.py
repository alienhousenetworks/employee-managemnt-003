import uuid
from django.conf import settings
from django.db import models
from apps.organizations.models import Organization

class ApprovalRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="approval_requests")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requested_approvals")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="decided_approvals")
    action_type = models.CharField(max_length=100)
    target_type = models.CharField(max_length=80)
    target_id = models.CharField(max_length=100, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    reason = models.TextField(max_length=4000)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    decision_note = models.TextField(max_length=4000, blank=True)
    idempotency_key = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        indexes = [models.Index(fields=["organization", "status", "created_at"])]
        constraints = [models.UniqueConstraint(fields=["organization", "requested_by", "idempotency_key"], condition=~models.Q(idempotency_key=""), name="uniq_approval_idempotency")]

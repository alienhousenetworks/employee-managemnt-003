import uuid
from django.conf import settings
from django.db import models
from apps.organizations.models import Organization

class EmployeeProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="employee_profiles")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profiles")
    employee_code = models.CharField(max_length=40)
    display_name = models.CharField(max_length=160)
    job_title = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="direct_reports")
    business_phone = models.CharField(max_length=40, blank=True)
    skills = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "employee_code"], name="uniq_employee_code_per_org"), models.UniqueConstraint(fields=["organization", "user"], name="uniq_employee_user_per_org")]
        indexes = [models.Index(fields=["organization", "department", "is_active"])]

class DirectMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="direct_messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_agency_messages")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_agency_messages")
    body = models.TextField(max_length=10000)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["-sent_at"]
        indexes = [models.Index(fields=["organization", "sender", "recipient", "sent_at"])]

class Notification(models.Model):
    class Kind(models.TextChoices):
        ASSIGNMENT = "ASSIGNMENT", "Assignment"
        APPROVAL = "APPROVAL", "Approval"
        MESSAGE = "MESSAGE", "Message"
        HR = "HR", "HR update"
        SYSTEM = "SYSTEM", "System"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="notifications")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agency_notifications")
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.SYSTEM)
    title = models.CharField(max_length=180)
    body = models.CharField(max_length=2000, blank=True)
    target_type = models.CharField(max_length=80, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "recipient", "read_at", "created_at"])]

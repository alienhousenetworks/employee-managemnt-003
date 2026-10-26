import uuid
from django.conf import settings
from django.db import models
from apps.organizations.models import Organization

class WhatsAppIntegration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="whatsapp_integrations")
    phone_number_id = models.CharField(max_length=100, unique=True)
    display_phone_number = models.CharField(max_length=40, blank=True)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class WhatsAppContact(models.Model):
    class Consent(models.TextChoices):
        UNKNOWN = "UNKNOWN", "Unknown"
        OPTED_IN = "OPTED_IN", "Opted in"
        OPTED_OUT = "OPTED_OUT", "Opted out"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="whatsapp_contacts")
    phone_e164 = models.CharField(max_length=20)
    display_name = models.CharField(max_length=160, blank=True)
    consent = models.CharField(max_length=12, choices=Consent.choices, default=Consent.UNKNOWN)
    consent_source = models.CharField(max_length=120, blank=True)
    consent_recorded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "phone_e164"], name="uniq_whatsapp_contact_per_org")]

class WhatsAppMessage(models.Model):
    class Direction(models.TextChoices):
        INBOUND = "INBOUND", "Inbound"
        OUTBOUND = "OUTBOUND", "Outbound"
    class Status(models.TextChoices):
        RECEIVED = "RECEIVED", "Received"
        NEEDS_REVIEW = "NEEDS_REVIEW", "Needs review"
        QUEUED = "QUEUED", "Queued for approval"
        APPROVED = "APPROVED", "Approved for sending"
        SENT = "SENT", "Sent"
        DELIVERED = "DELIVERED", "Delivered"
        READ = "READ", "Read"
        FAILED = "FAILED", "Failed"
        REJECTED = "REJECTED", "Rejected"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="whatsapp_messages")
    contact = models.ForeignKey(WhatsAppContact, on_delete=models.CASCADE, related_name="messages")
    direction = models.CharField(max_length=8, choices=Direction.choices)
    provider_message_id = models.CharField(max_length=160, null=True, blank=True, unique=True)
    body = models.TextField(max_length=10000, blank=True)
    template_name = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_whatsapp_messages")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_whatsapp_messages")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "status", "created_at"])]

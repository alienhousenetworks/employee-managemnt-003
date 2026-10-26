import uuid
from django.conf import settings
from django.db import models
from apps.organizations.models import Organization

class EODReport(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        IN_REVIEW = "IN_REVIEW", "In review"
        NEEDS_CHANGES = "NEEDS_CHANGES", "Needs changes"
        APPROVED = "APPROVED", "Approved"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="eod_reports")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eod_reports")
    report_date = models.DateField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    completed_work = models.TextField(blank=True)
    in_progress = models.TextField(blank=True)
    blockers = models.TextField(blank=True)
    next_day_priorities = models.TextField(blank=True)
    evidence = models.JSONField(default=list, blank=True)
    version = models.PositiveIntegerField(default=1)
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_eod_reports")
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "employee", "report_date", "version"], name="uniq_eod_report_version")]
        ordering = ["-report_date", "-version"]

class EODRevision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(EODReport, on_delete=models.CASCADE, related_name="revisions")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    previous_status = models.CharField(max_length=16, blank=True)
    new_status = models.CharField(max_length=16)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

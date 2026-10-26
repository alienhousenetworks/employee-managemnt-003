import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
from apps.organizations.models import Organization

class AttendanceEntry(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Clocked in"
        CLOSED = "CLOSED", "Clocked out"
        CORRECTION_REQUESTED = "CORRECTION_REQUESTED", "Correction requested"
        APPROVED = "APPROVED", "Approved"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="attendance_entries")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_entries")
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.OPEN)
    note = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [models.Index(fields=["organization", "employee", "started_at"])]

class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="leave_requests")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_requests")
    leave_type = models.CharField(max_length=40)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(max_length=3000, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUBMITTED)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_leave_requests")
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["organization", "employee", "status"])]

class EmployeeRequest(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        IN_REVIEW = "IN_REVIEW", "In review"
        COMPLETED = "COMPLETED", "Completed"
        REJECTED = "REJECTED", "Rejected"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="employee_requests")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_requests")
    request_type = models.CharField(max_length=60)
    title = models.CharField(max_length=200)
    details = models.TextField(max_length=5000, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUBMITTED)
    created_at = models.DateTimeField(auto_now_add=True)

class ShiftSchedule(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="shift_schedules")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="shift_schedules")
    shift_date = models.DateField()
    starts_at = models.TimeField()
    ends_at = models.TimeField()
    timezone_name = models.CharField(max_length=64, default="Asia/Kolkata")
    note = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_shift_schedules")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "employee", "shift_date"], name="uniq_employee_shift_per_day")]
        indexes = [models.Index(fields=["organization", "shift_date"])]

class LeaveBalance(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="leave_balances")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leave_balances")
    leave_type = models.CharField(max_length=40)
    period_start = models.DateField()
    period_end = models.DateField()
    entitled_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    accrued_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    used_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    adjusted_days = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "employee", "leave_type", "period_start", "period_end"], name="uniq_leave_balance_period")]

class AttendanceCorrectionRequest(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="attendance_corrections")
    attendance = models.ForeignKey(AttendanceEntry, on_delete=models.CASCADE, related_name="correction_requests")
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_corrections")
    proposed_start = models.DateTimeField(null=True, blank=True)
    proposed_end = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(max_length=2000)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUBMITTED)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_attendance_corrections")
    review_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

class Candidate(models.Model):
    class Stage(models.TextChoices):
        SOURCED = "SOURCED", "Sourced"
        SCREENED = "SCREENED", "Screened"
        INTERVIEWING = "INTERVIEWING", "Interviewing"
        OFFER = "OFFER", "Offer"
        HIRED = "HIRED", "Hired"
        REJECTED = "REJECTED", "Rejected"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="candidates")
    full_name = models.CharField(max_length=180)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    role_title = models.CharField(max_length=180)
    source = models.CharField(max_length=100, blank=True)
    stage = models.CharField(max_length=16, choices=Stage.choices, default=Stage.SOURCED)
    resume_url = models.URLField(blank=True)
    notes = models.TextField(max_length=4000, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="owned_candidates")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "email", "role_title"], name="uniq_candidate_role_email")]

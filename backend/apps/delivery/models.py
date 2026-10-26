import uuid
from django.conf import settings
from django.db import models
from apps.organizations.models import Organization

class ClientAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="clients")
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=24, default="ACTIVE")
    account_owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "name"], name="uniq_client_name_per_org")]

class Project(models.Model):
    class Status(models.TextChoices):
        PLANNING = "PLANNING", "Planning"
        ACTIVE = "ACTIVE", "Active"
        BLOCKED = "BLOCKED", "Blocked"
        IN_REVIEW = "IN_REVIEW", "In review"
        COMPLETED = "COMPLETED", "Completed"
        ARCHIVED = "ARCHIVED", "Archived"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="projects")
    client = models.ForeignKey(ClientAccount, null=True, blank=True, on_delete=models.PROTECT, related_name="projects")
    name = models.CharField(max_length=200)
    service_line = models.CharField(max_length=40)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PLANNING)
    project_manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [models.Index(fields=["organization", "status"])]

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "TODO", "To do"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        BLOCKED = "BLOCKED", "Blocked"
        IN_REVIEW = "IN_REVIEW", "In review"
        DONE = "DONE", "Done"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="tasks")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    acceptance_criteria = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=12, default="MEDIUM")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="agency_tasks")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_agency_tasks")
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [models.Index(fields=["organization", "status", "due_date"])]

class TaskDependency(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="task_dependencies")
    predecessor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="blocking_dependencies")
    successor = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="blocked_dependencies")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["predecessor", "successor"], name="uniq_task_dependency_pair"),
            models.CheckConstraint(condition=~models.Q(predecessor=models.F("successor")), name="task_cannot_depend_on_self"),
        ]
        indexes = [models.Index(fields=["organization", "successor"])]

class ProjectDeliverable(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        READY_FOR_QA = "READY_FOR_QA", "Ready for QA"
        QA_FAILED = "QA_FAILED", "QA failed"
        APPROVED = "APPROVED", "Approved"
        DELIVERED = "DELIVERED", "Delivered"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="project_deliverables")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="deliverables")
    title = models.CharField(max_length=240)
    description = models.TextField(blank=True)
    acceptance_criteria = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    version = models.PositiveIntegerField(default=1)
    evidence_url = models.URLField(blank=True)
    qa_notes = models.TextField(blank=True, max_length=4000)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_deliverables")
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_deliverables")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["organization", "project", "status"])]

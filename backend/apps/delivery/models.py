import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone
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

class ServiceTemplate(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="service_templates")
    service_line = models.CharField(max_length=40)
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    default_tasks = models.JSONField(default=list, blank=True)
    default_deliverables = models.JSONField(default=list, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "service_line", "name"], name="uniq_service_template")]

class Opportunity(models.Model):
    class Stage(models.TextChoices):
        LEAD = "LEAD", "Lead"
        QUALIFIED = "QUALIFIED", "Qualified"
        DISCOVERY = "DISCOVERY", "Discovery"
        PROPOSAL = "PROPOSAL", "Proposal"
        NEGOTIATION = "NEGOTIATION", "Negotiation"
        WON = "WON", "Won"
        LOST = "LOST", "Lost"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="opportunities")
    client = models.ForeignKey(ClientAccount, null=True, blank=True, on_delete=models.PROTECT, related_name="opportunities")
    name = models.CharField(max_length=200)
    source = models.CharField(max_length=100, blank=True)
    service_line = models.CharField(max_length=40)
    stage = models.CharField(max_length=16, choices=Stage.choices, default=Stage.LEAD)
    estimated_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="INR")
    probability_percent = models.PositiveSmallIntegerField(default=0)
    next_action = models.CharField(max_length=240, blank=True)
    next_action_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="owned_opportunities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        indexes = [models.Index(fields=["organization", "stage", "next_action_date"])]

class ClientRenewal(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        RENEWED = "RENEWED", "Renewed"
        CHURNED = "CHURNED", "Churned"
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="client_renewals")
    client = models.ForeignKey(ClientAccount, on_delete=models.CASCADE, related_name="renewals")
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL, related_name="renewals")
    renewal_date = models.DateField()
    contract_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GitHubRepositoryLink(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="github_repository_links")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="github_repositories")
    repository_full_name = models.CharField(max_length=240)
    repository_url = models.URLField()
    installation_id = models.CharField(max_length=100, blank=True)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "repository_full_name"], name="uniq_github_repo_per_org")]

class GitHubWorkItemLink(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="github_work_item_links")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="github_work_items")
    repository = models.ForeignKey(GitHubRepositoryLink, on_delete=models.CASCADE, related_name="work_items")
    external_id = models.CharField(max_length=100)
    item_type = models.CharField(max_length=20, default="issue")
    title = models.CharField(max_length=240, blank=True)
    url = models.URLField()
    state = models.CharField(max_length=40, blank=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["repository", "external_id", "item_type"], name="uniq_github_work_item")]


class GitHubWebhookDelivery(models.Model):
    """Durable idempotency ledger for signed GitHub webhook deliveries."""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="github_webhook_deliveries")
    delivery_id = models.CharField(max_length=120)
    event_name = models.CharField(max_length=80)
    payload_sha256 = models.CharField(max_length=64)
    processed = models.BooleanField(default=False)
    received_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "delivery_id"],
                name="uniq_github_delivery_per_org",
            )
        ]
        indexes = [models.Index(fields=["organization", "processed", "received_at"])]

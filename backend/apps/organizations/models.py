import uuid
from django.conf import settings
from django.db import models

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name

class Membership(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Agency owner"
        ADMIN = "ADMIN", "Administrator"
        HR = "HR", "HR administrator"
        FINANCE = "FINANCE", "Finance manager"
        SALES = "SALES", "Sales manager"
        MANAGER = "MANAGER", "Manager"
        EMPLOYEE = "EMPLOYEE", "Employee"
        CLIENT = "CLIENT", "Client collaborator"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agency_memberships")
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["organization", "user"], name="uniq_org_membership")]
        indexes = [models.Index(fields=["organization", "is_active"])]

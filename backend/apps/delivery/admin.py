from django.contrib import admin
from .models import (
    ClientAccount, Project, Task, TaskDependency, ProjectDeliverable,
    ServiceTemplate, Opportunity, ClientRenewal, GitHubRepositoryLink,
    GitHubWorkItemLink, GitHubWebhookDelivery,
)


@admin.register(ClientAccount)
class ClientAccountAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "status", "account_owner", "created_at")
    list_filter = ("organization", "status")
    search_fields = ("name",)
    autocomplete_fields = ("organization", "account_owner")
    readonly_fields = ("id", "created_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "client", "service_line", "status", "project_manager", "due_date")
    list_filter = ("organization", "service_line", "status")
    search_fields = ("name", "client__name")
    autocomplete_fields = ("organization", "client", "project_manager")
    readonly_fields = ("id", "created_at")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "project", "status", "priority", "assignee", "due_date")
    list_filter = ("organization", "status", "priority")
    search_fields = ("title", "description", "project__name")
    autocomplete_fields = ("organization", "project", "assignee", "created_by")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ("organization", "predecessor", "successor", "created_by", "created_at")
    list_filter = ("organization",)
    readonly_fields = ("created_at",)


@admin.register(ProjectDeliverable)
class ProjectDeliverableAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "project", "status", "version", "approved_by", "updated_at")
    list_filter = ("organization", "status")
    search_fields = ("title", "project__name")
    readonly_fields = ("id", "created_at", "updated_at", "approved_by")
    autocomplete_fields = ("organization", "project", "created_by")


@admin.register(ServiceTemplate)
class ServiceTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "service_line", "active", "created_at")
    list_filter = ("organization", "service_line", "active")
    search_fields = ("name", "description")
    readonly_fields = ("created_at",)


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "client", "service_line", "stage", "estimated_value", "owner", "next_action_date")
    list_filter = ("organization", "service_line", "stage")
    search_fields = ("name", "client__name", "source")
    autocomplete_fields = ("organization", "client", "owner")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ClientRenewal)
class ClientRenewalAdmin(admin.ModelAdmin):
    list_display = ("client", "organization", "project", "renewal_date", "status", "contract_value", "owner")
    list_filter = ("organization", "status", "renewal_date")
    search_fields = ("client__name", "project__name")
    autocomplete_fields = ("organization", "client", "project", "owner")
    readonly_fields = ("created_at",)


@admin.register(GitHubRepositoryLink)
class GitHubRepositoryLinkAdmin(admin.ModelAdmin):
    list_display = ("repository_full_name", "organization", "project", "installation_id", "is_enabled")
    list_filter = ("organization", "is_enabled")
    search_fields = ("repository_full_name",)
    readonly_fields = ("created_at",)


@admin.register(GitHubWorkItemLink)
class GitHubWorkItemLinkAdmin(admin.ModelAdmin):
    list_display = ("repository", "external_id", "item_type", "title", "state", "synced_at")
    list_filter = ("organization", "item_type", "state")
    search_fields = ("title", "external_id")
    readonly_fields = ("created_at", "synced_at")


@admin.register(GitHubWebhookDelivery)
class GitHubWebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ("organization", "delivery_id", "event_name", "processed", "received_at", "processed_at")
    list_filter = ("organization", "event_name", "processed", "received_at")
    search_fields = ("delivery_id", "payload_sha256")
    readonly_fields = ("organization", "delivery_id", "event_name", "payload_sha256", "processed", "received_at", "processed_at")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return request.user.is_superuser and super().has_change_permission(request, obj)
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser and super().has_delete_permission(request, obj)

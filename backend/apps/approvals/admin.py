from django.contrib import admin
from .models import ApprovalRequest


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ("action_type", "organization", "requested_by", "reviewer", "status", "created_at", "decided_at")
    list_filter = ("organization", "action_type", "status", "created_at")
    search_fields = ("target_type", "target_id", "reason", "requested_by__username")
    readonly_fields = ("id", "organization", "requested_by", "action_type", "target_type", "target_id", "payload", "reason", "status", "reviewer", "decision_note", "idempotency_key", "created_at", "decided_at")
    autocomplete_fields = ("reviewer",)
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser and super().has_delete_permission(request, obj)

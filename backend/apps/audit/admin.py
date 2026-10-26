from django.contrib import admin
from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "organization", "actor", "action", "object_type", "object_id", "outcome", "request_id")
    list_filter = ("organization", "action", "outcome", "created_at")
    search_fields = ("object_type", "object_id", "request_id", "actor__username")
    readonly_fields = ("id", "organization", "actor", "action", "object_type", "object_id", "request_id", "outcome", "metadata", "created_at")
    ordering = ("-created_at",)
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

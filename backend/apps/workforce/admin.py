from django.contrib import admin
from .models import EmployeeProfile, DirectMessage, Notification


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "employee_code", "organization", "job_title", "department", "manager", "is_active")
    list_filter = ("organization", "department", "is_active")
    search_fields = ("display_name", "employee_code", "user__username", "user__email")
    autocomplete_fields = ("organization", "user", "manager")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ("organization", "sender", "recipient", "sent_at", "read_at")
    list_filter = ("organization", "sent_at")
    search_fields = ("sender__username", "recipient__username", "body")
    readonly_fields = ("id", "organization", "sender", "recipient", "body", "sent_at", "read_at")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return request.user.is_superuser and super().has_change_permission(request, obj)
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser and super().has_delete_permission(request, obj)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "recipient", "kind", "created_at", "read_at")
    list_filter = ("organization", "kind", "created_at")
    search_fields = ("title", "body", "recipient__username")
    readonly_fields = ("id", "created_at", "read_at")

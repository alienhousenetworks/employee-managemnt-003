from django.contrib import admin
from .models import EODReport, EODRevision


@admin.register(EODReport)
class EODReportAdmin(admin.ModelAdmin):
    list_display = ("employee", "organization", "report_date", "version", "status", "submitted_at", "reviewed_by")
    list_filter = ("organization", "status", "report_date")
    search_fields = ("employee__username", "completed_work", "blockers")
    readonly_fields = ("id", "organization", "employee", "report_date", "version", "submitted_at", "created_at", "updated_at")
    autocomplete_fields = ("reviewed_by",)
    def has_add_permission(self, request): return False


@admin.register(EODRevision)
class EODRevisionAdmin(admin.ModelAdmin):
    list_display = ("report", "actor", "previous_status", "new_status", "created_at")
    list_filter = ("new_status", "created_at")
    readonly_fields = ("report", "actor", "previous_status", "new_status", "note", "created_at")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return request.user.is_superuser and super().has_delete_permission(request, obj)

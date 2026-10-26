from django.contrib import admin
from .models import (
    AttendanceEntry, LeaveRequest, EmployeeRequest, ShiftSchedule,
    LeaveBalance, AttendanceCorrectionRequest, Candidate,
)


@admin.register(AttendanceEntry)
class AttendanceEntryAdmin(admin.ModelAdmin):
    list_display = ("employee", "organization", "started_at", "ended_at", "status")
    list_filter = ("organization", "status", "started_at")
    search_fields = ("employee__username", "employee__email", "note")
    readonly_fields = ("id", "organization", "employee", "started_at", "ended_at", "status", "created_at")
    autocomplete_fields = ("organization", "employee")


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "organization", "leave_type", "start_date", "end_date", "status", "reviewer")
    list_filter = ("organization", "leave_type", "status")
    search_fields = ("employee__username", "employee__email", "reason")
    readonly_fields = ("id", "organization", "employee", "leave_type", "start_date", "end_date", "reason", "status", "reviewer", "review_note", "created_at", "updated_at")
    autocomplete_fields = ("organization", "employee", "reviewer")


@admin.register(EmployeeRequest)
class EmployeeRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "employee", "request_type", "status", "created_at")
    list_filter = ("organization", "request_type", "status")
    search_fields = ("title", "employee__username", "details")
    readonly_fields = ("id", "created_at")


@admin.register(ShiftSchedule)
class ShiftScheduleAdmin(admin.ModelAdmin):
    list_display = ("employee", "organization", "shift_date", "starts_at", "ends_at", "timezone_name")
    list_filter = ("organization", "shift_date")
    search_fields = ("employee__username", "note")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("organization", "employee", "created_by")


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "organization", "leave_type", "period_start", "period_end", "entitled_days", "accrued_days", "used_days")
    list_filter = ("organization", "leave_type", "period_start")
    search_fields = ("employee__username",)
    readonly_fields = ("updated_at",)


@admin.register(AttendanceCorrectionRequest)
class AttendanceCorrectionRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "organization", "attendance", "status", "created_at", "reviewed_by")
    list_filter = ("organization", "status", "created_at")
    search_fields = ("employee__username", "reason")
    readonly_fields = ("organization", "attendance", "employee", "proposed_start", "proposed_end", "reason", "status", "reviewed_by", "review_note", "created_at", "reviewed_at")
    autocomplete_fields = ("organization", "attendance", "employee", "reviewed_by")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("full_name", "organization", "role_title", "stage", "owner", "created_at")
    list_filter = ("organization", "stage", "source")
    search_fields = ("full_name", "email", "role_title")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("organization", "owner")

from rest_framework import serializers
from .models import AttendanceEntry, LeaveRequest, EmployeeRequest

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceEntry
        fields = ["id", "started_at", "ended_at", "status", "note", "created_at"]
        read_only_fields = ["id", "started_at", "ended_at", "status", "created_at"]
class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ["id", "leave_type", "start_date", "end_date", "reason", "status", "reviewer", "review_note", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "reviewer", "review_note", "created_at", "updated_at"]
    def validate(self, attrs):
        if attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError({"end_date":"End date cannot be before start date."})
        return attrs
class EmployeeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeRequest
        fields = ["id", "request_type", "title", "details", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

from .models import ShiftSchedule, LeaveBalance

class ShiftScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftSchedule
        fields = ["id", "employee", "shift_date", "starts_at", "ends_at", "timezone_name", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]

class LeaveBalanceSerializer(serializers.ModelSerializer):
    available_days = serializers.SerializerMethodField()
    class Meta:
        model = LeaveBalance
        fields = ["id", "employee", "leave_type", "period_start", "period_end", "entitled_days", "accrued_days", "used_days", "adjusted_days", "available_days", "updated_at"]
        read_only_fields = fields
    def get_available_days(self, obj):
        return obj.entitled_days + obj.accrued_days + obj.adjusted_days - obj.used_days

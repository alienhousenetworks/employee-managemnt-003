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

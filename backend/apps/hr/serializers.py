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
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be before start date."})
        employee = self.context["request"].user
        organization = getattr(self.context["request"], "organization", None)
        if start_date and end_date and organization:
            # Draft/submitted/approved leave blocks overlapping requests. Rejected
            # and cancelled requests do not. Exclude this row for safe future edits.
            conflicts = LeaveRequest.objects.filter(
                organization=organization,
                employee=employee,
                status__in=[LeaveRequest.Status.SUBMITTED, LeaveRequest.Status.APPROVED],
                start_date__lte=end_date,
                end_date__gte=start_date,
            )
            if self.instance:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            if conflicts.exists():
                raise serializers.ValidationError({
                    "start_date": "This date range overlaps an existing submitted or approved leave request."
                })
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

from .models import AttendanceCorrectionRequest, Candidate

class AttendanceCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceCorrectionRequest
        fields = ["id", "attendance", "proposed_start", "proposed_end", "reason", "status", "reviewed_by", "review_note", "created_at", "reviewed_at"]
        read_only_fields = ["id", "status", "reviewed_by", "review_note", "created_at", "reviewed_at"]
    def validate(self, attrs):
        start = attrs.get("proposed_start")
        end = attrs.get("proposed_end")
        if start and end and end <= start:
            raise serializers.ValidationError({"proposed_end": "Corrected end must be after corrected start."})
        return attrs

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ["id", "full_name", "email", "phone", "role_title", "source", "stage", "resume_url", "notes", "owner", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

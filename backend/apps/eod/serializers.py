from rest_framework import serializers
from .models import EODReport

class EODReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EODReport
        fields = ["id", "employee", "report_date", "status", "completed_work", "in_progress", "blockers", "next_day_priorities", "evidence", "version", "submitted_at", "reviewed_by", "review_note", "created_at", "updated_at"]
        read_only_fields = ["id", "employee", "status", "version", "submitted_at", "reviewed_by", "review_note", "created_at", "updated_at"]

    def validate_evidence(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Evidence must be a list of structured evidence records.")
        if len(value) > 30:
            raise serializers.ValidationError("A report can include at most 30 evidence records.")
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError({index: "Each evidence record must be an object."})
            if not str(item.get("title", "")).strip():
                raise serializers.ValidationError({index: "Evidence title is required."})
            if not str(item.get("type", "")).strip():
                raise serializers.ValidationError({index: "Evidence type is required."})
            if not str(item.get("reference", "")).strip():
                raise serializers.ValidationError({index: "Evidence reference is required."})
            # Client-provided evidence is a claim, not proof of verification.
            if item.get("verification_status") in {"VERIFIED", "LIVE_VERIFIED"}:
                raise serializers.ValidationError({index: "Verification status is assigned by server-side verification, not by the client."})
        return value

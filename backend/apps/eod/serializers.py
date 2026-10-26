from rest_framework import serializers
from .models import EODReport

class EODReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = EODReport
        fields = ["id", "employee", "report_date", "status", "completed_work", "in_progress", "blockers", "next_day_priorities", "evidence", "version", "submitted_at", "reviewed_by", "review_note", "created_at", "updated_at"]
        read_only_fields = ["id", "employee", "status", "version", "submitted_at", "reviewed_by", "review_note", "created_at", "updated_at"]

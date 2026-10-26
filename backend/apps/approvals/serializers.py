from rest_framework import serializers
from .models import ApprovalRequest

class ApprovalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequest
        fields = ["id", "requested_by", "reviewer", "action_type", "target_type", "target_id", "payload", "reason", "status", "decision_note", "idempotency_key", "created_at", "decided_at"]
        read_only_fields = ["id", "requested_by", "reviewer", "status", "decision_note", "created_at", "decided_at"]
    def validate_payload(self, value):
        if not isinstance(value, dict): raise serializers.ValidationError("Payload must be a JSON object.")
        if len(str(value)) > 20000: raise serializers.ValidationError("Payload is too large.")
        return value

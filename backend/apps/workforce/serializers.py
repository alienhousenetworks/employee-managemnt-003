from rest_framework import serializers
from .models import EmployeeProfile, DirectMessage, Notification

class EmployeeProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    class Meta:
        model = EmployeeProfile
        fields = ["id", "user_id", "employee_code", "display_name", "job_title", "department", "manager", "business_phone", "skills", "is_active", "created_at"]
        read_only_fields = ["id", "created_at", "is_active", "manager"]

class DirectMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_username", read_only=True)
    recipient_name = serializers.CharField(source="recipient.get_username", read_only=True)
    class Meta:
        model = DirectMessage
        fields = ["id", "sender", "sender_name", "recipient", "recipient_name", "body", "sent_at", "read_at"]
        read_only_fields = ["id", "sender", "sender_name", "recipient_name", "sent_at", "read_at"]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "kind", "title", "body", "target_type", "target_id", "created_at", "read_at"]
        read_only_fields = fields

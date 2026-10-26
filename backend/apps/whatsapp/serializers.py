from rest_framework import serializers
from .models import WhatsAppContact, WhatsAppMessage

class WhatsAppContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppContact
        fields = ["id", "phone_e164", "display_name", "consent", "consent_source", "consent_recorded_at", "created_at"]
        read_only_fields = ["id", "consent", "consent_source", "consent_recorded_at", "created_at"]

class WhatsAppMessageSerializer(serializers.ModelSerializer):
    contact_phone = serializers.CharField(source="contact.phone_e164", read_only=True)
    class Meta:
        model = WhatsAppMessage
        fields = ["id", "contact", "contact_phone", "direction", "provider_message_id", "body", "template_name", "status", "created_by", "approved_by", "created_at", "updated_at"]
        read_only_fields = ["id", "contact_phone", "direction", "provider_message_id", "status", "created_by", "approved_by", "created_at", "updated_at"]

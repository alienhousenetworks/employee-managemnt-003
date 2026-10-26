import hashlib
import hmac
import json
import os
from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import WhatsAppIntegration, WhatsAppContact, WhatsAppMessage
from .serializers import WhatsAppContactSerializer, WhatsAppMessageSerializer

class WhatsAppWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN")
        if not verify_token:
            return Response({"status": "NOT_CONFIGURED"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        if request.query_params.get("hub.mode") == "subscribe" and hmac.compare_digest(request.query_params.get("hub.verify_token", ""), verify_token):
            return Response(request.query_params.get("hub.challenge", ""), content_type="text/plain")
        return Response({"detail": "Webhook verification failed."}, status=status.HTTP_403_FORBIDDEN)

    @transaction.atomic
    def post(self, request):
        app_secret = os.environ.get("WHATSAPP_APP_SECRET")
        if not app_secret:
            return Response({"status": "NOT_CONFIGURED"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        supplied = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(app_secret.encode(), request.body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(supplied, expected):
            return Response({"detail": "Invalid webhook signature."}, status=status.HTTP_403_FORBIDDEN)
        try:
            payload = json.loads(request.body)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid JSON payload."}, status=status.HTTP_400_BAD_REQUEST)
        processed = 0
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                phone_number_id = value.get("metadata", {}).get("phone_number_id")
                integration = WhatsAppIntegration.objects.filter(phone_number_id=phone_number_id, is_enabled=True, organization__is_active=True).first()
                if not integration:
                    continue
                for message in value.get("messages", []):
                    provider_id = message.get("id")
                    sender_phone = message.get("from")
                    if not provider_id or not sender_phone:
                        continue
                    if WhatsAppMessage.objects.filter(provider_message_id=provider_id).exists():
                        continue
                    profile = next((c.get("profile", {}).get("name", "") for c in value.get("contacts", []) if c.get("wa_id") == sender_phone), "")
                    contact, _ = WhatsAppContact.objects.get_or_create(
                        organization=integration.organization, phone_e164="+" + sender_phone.lstrip("+"),
                        defaults={"display_name": profile},
                    )
                    text_body = message.get("text", {}).get("body", "")
                    if not text_body and message.get("type") != "text":
                        text_body = "[Non-text WhatsApp message received; media processing is not configured.]"
                    WhatsAppMessage.objects.create(
                        organization=integration.organization, contact=contact, direction=WhatsAppMessage.Direction.INBOUND,
                        provider_message_id=provider_id, body=text_body, status=WhatsAppMessage.Status.RECEIVED,
                    )
                    processed += 1
                for delivery in value.get("statuses", []):
                    provider_id = delivery.get("id")
                    provider_status = delivery.get("status")
                    mapping = {"sent": "SENT", "delivered": "DELIVERED", "read": "READ", "failed": "FAILED"}
                    if provider_id and provider_status in mapping:
                        WhatsAppMessage.objects.filter(
                            organization=integration.organization, provider_message_id=provider_id,
                            direction=WhatsAppMessage.Direction.OUTBOUND,
                        ).update(status=mapping[provider_status], updated_at=timezone.now())
        return Response({"accepted": True, "processed_inbound": processed}, status=status.HTTP_200_OK)

class WhatsAppContactListCreateView(generics.ListCreateAPIView):
    serializer_class = WhatsAppContactSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        return WhatsAppContact.objects.filter(organization=self.request.organization).order_by("-created_at")
    def perform_create(self, serializer):
        phone = serializer.validated_data.get("phone_e164", "")
        if not phone.startswith("+") or not phone[1:].isdigit() or not 8 <= len(phone[1:]) <= 15:
            raise ValidationError({"phone_e164": "Use an E.164 phone number such as +14155550123."})
        serializer.save(organization=self.request.organization)

class WhatsAppConsentView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def post(self, request, contact_id):
        contact = WhatsAppContact.objects.filter(id=contact_id, organization=request.organization).first()
        if not contact:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        action = request.data.get("action")
        source = str(request.data.get("source", "")).strip()[:120]
        if action not in {"opt_in", "opt_out"} or not source:
            raise ValidationError({"consent": "Provide action opt_in or opt_out and a non-empty source."})
        contact.consent = WhatsAppContact.Consent.OPTED_IN if action == "opt_in" else WhatsAppContact.Consent.OPTED_OUT
        contact.consent_source = source
        contact.consent_recorded_at = timezone.now()
        contact.save(update_fields=["consent", "consent_source", "consent_recorded_at"])
        return Response(WhatsAppContactSerializer(contact).data)

class WhatsAppMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = WhatsAppMessageSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        return WhatsAppMessage.objects.filter(organization=self.request.organization).select_related("contact").order_by("-created_at")
    def perform_create(self, serializer):
        contact = serializer.validated_data["contact"]
        if contact.organization_id != self.request.organization.id:
            raise ValidationError({"contact": "Contact must belong to the active organization."})
        if contact.consent != WhatsAppContact.Consent.OPTED_IN:
            raise ValidationError({"consent": "Outbound messages require recorded opt-in consent."})
        # Fail closed: outbound messages must use a template explicitly allowlisted
        # by the operator after approval in Meta WhatsApp Manager. Never treat a
        # client-supplied template name as proof of provider approval.
        template = serializer.validated_data.get("template_name", "").strip()
        configured = {
            name.strip()
            for name in os.environ.get("WHATSAPP_APPROVED_TEMPLATES", "").split(",")
            if name.strip()
        }
        if not configured:
            raise ValidationError({"template_name": "Approved WhatsApp templates are not configured."})
        if not template or template not in configured:
            raise ValidationError({"template_name": "Use a template name in the configured approved-template allowlist."})
        serializer.save(
            body="", organization=self.request.organization,
            direction=WhatsAppMessage.Direction.OUTBOUND,
            status=WhatsAppMessage.Status.QUEUED, created_by=self.request.user,
        )

class WhatsAppMessageApprovalView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def post(self, request, message_id):
        if request.membership.role not in {"OWNER", "ADMIN", "MANAGER", "SALES"}:
            raise PermissionDenied("A manager must approve outbound WhatsApp messages.")
        message = WhatsAppMessage.objects.filter(id=message_id, organization=request.organization, direction=WhatsAppMessage.Direction.OUTBOUND).first()
        if not message:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if message.status != WhatsAppMessage.Status.QUEUED:
            raise ValidationError({"status": "Only queued messages can be approved."})
        if message.contact.consent != WhatsAppContact.Consent.OPTED_IN:
            raise ValidationError({"consent": "Contact opt-in is required at approval time."})
        configured = {
            name.strip()
            for name in os.environ.get("WHATSAPP_APPROVED_TEMPLATES", "").split(",")
            if name.strip()
        }
        if not configured or not message.template_name or message.template_name not in configured:
            raise ValidationError({"template_name": "The message template is not currently allowlisted."})
        message.status = WhatsAppMessage.Status.APPROVED
        message.approved_by = request.user
        message.save(update_fields=["status", "approved_by", "updated_at"])
        # APPROVED is not SENT: a provider-backed worker must perform delivery.
        return Response(WhatsAppMessageSerializer(message).data)

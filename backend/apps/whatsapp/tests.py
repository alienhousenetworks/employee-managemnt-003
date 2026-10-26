import hashlib
import hmac
import json
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.organizations.models import Organization, Membership
from .models import WhatsAppIntegration, WhatsAppContact, WhatsAppMessage

@pytest.mark.django_db
def test_webhook_fails_closed_when_secret_is_not_configured(settings, monkeypatch):
    monkeypatch.delenv("WHATSAPP_APP_SECRET", raising=False)
    response = APIClient().generic("POST", "/api/v1/whatsapp/webhook/", data=b'{"entry":[]}', content_type="application/json")
    assert response.status_code == 503
    assert response.data["status"] == "NOT_CONFIGURED"

@pytest.mark.django_db
def test_webhook_rejects_invalid_signature(settings, monkeypatch):
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "test-secret")
    response = APIClient().generic("POST", "/api/v1/whatsapp/webhook/", data=b'{"entry":[]}', content_type="application/json", HTTP_X_HUB_SIGNATURE_256="sha256=invalid")
    assert response.status_code == 403

@pytest.mark.django_db
def test_signed_inbound_webhook_is_idempotent_and_does_not_infer_consent(monkeypatch):
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "test-secret")
    org = Organization.objects.create(name="WhatsApp Agency", slug="whatsapp-agency")
    WhatsAppIntegration.objects.create(organization=org, phone_number_id="phone-id-1", is_enabled=True)
    payload = {"entry": [{"changes": [{"value": {"metadata": {"phone_number_id": "phone-id-1"}, "contacts": [{"wa_id": "14155550123", "profile": {"name": "A Contact"}}], "messages": [{"id": "wamid.123", "from": "14155550123", "type": "text", "text": {"body": "Hello agency"}}]}}]}]}
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(b"test-secret", body, hashlib.sha256).hexdigest()
    client = APIClient()
    first = client.generic("POST", "/api/v1/whatsapp/webhook/", data=body, content_type="application/json", HTTP_X_HUB_SIGNATURE_256=signature)
    second = client.generic("POST", "/api/v1/whatsapp/webhook/", data=body, content_type="application/json", HTTP_X_HUB_SIGNATURE_256=signature)
    assert first.status_code == 200
    assert first.data["processed_inbound"] == 1
    assert second.data["processed_inbound"] == 0
    contact = WhatsAppContact.objects.get(organization=org, phone_e164="+14155550123")
    assert contact.consent == WhatsAppContact.Consent.UNKNOWN
    assert WhatsAppMessage.objects.filter(provider_message_id="wamid.123").count() == 1

@pytest.mark.django_db
def test_outbound_requires_opt_in_and_manager_approval(monkeypatch):
    User = get_user_model()
    employee = User.objects.create_user(username="wa-employee", password="strong-password-123")
    manager = User.objects.create_user(username="wa-manager", password="strong-password-123")
    org = Organization.objects.create(name="Consent Agency", slug="consent-agency")
    Membership.objects.create(organization=org, user=employee, role="EMPLOYEE")
    Membership.objects.create(organization=org, user=manager, role="MANAGER")
    contact = WhatsAppContact.objects.create(organization=org, phone_e164="+14155550124")
    client = APIClient()
    client.force_authenticate(employee)
    rejected = client.post("/api/v1/whatsapp/messages/", {"contact": str(contact.id), "body": "Hello"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert rejected.status_code == 400
    contact.consent = WhatsAppContact.Consent.OPTED_IN
    contact.consent_source = "signup form"
    contact.save(update_fields=["consent", "consent_source"])
    queued = client.post("/api/v1/whatsapp/messages/", {"contact": str(contact.id), "body": "Hello"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert queued.status_code == 201
    client.force_authenticate(manager)
    approved = client.post(f"/api/v1/whatsapp/messages/{queued.data['id']}/approve/", {}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert approved.status_code == 200
    assert approved.data["status"] == "APPROVED"

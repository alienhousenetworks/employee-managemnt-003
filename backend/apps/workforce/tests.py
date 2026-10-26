import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.organizations.models import Organization, Membership
from .models import DirectMessage, Notification

@pytest.mark.django_db
def test_direct_messages_are_limited_to_active_org_members_and_participants():
    User = get_user_model()
    sender = User.objects.create_user(username="sender", password="strong-password-123")
    recipient = User.objects.create_user(username="recipient", password="strong-password-123")
    outsider = User.objects.create_user(username="outsider", password="strong-password-123")
    org = Organization.objects.create(name="Agency One", slug="agency-one")
    other = Organization.objects.create(name="Agency Two", slug="agency-two")
    Membership.objects.create(organization=org, user=sender, role="EMPLOYEE")
    Membership.objects.create(organization=org, user=recipient, role="EMPLOYEE")
    Membership.objects.create(organization=other, user=outsider, role="EMPLOYEE")
    DirectMessage.objects.create(organization=org, sender=sender, recipient=recipient, body="private")
    DirectMessage.objects.create(organization=other, sender=outsider, recipient=sender, body="other tenant")
    client = APIClient()
    client.force_authenticate(sender)
    response = client.get("/api/v1/employees/messages/", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["body"] == "private"

@pytest.mark.django_db
def test_message_send_rejects_recipient_outside_active_organization():
    User = get_user_model()
    sender = User.objects.create_user(username="sender2", password="strong-password-123")
    outsider = User.objects.create_user(username="outsider2", password="strong-password-123")
    org = Organization.objects.create(name="Agency Three", slug="agency-three")
    other = Organization.objects.create(name="Agency Four", slug="agency-four")
    Membership.objects.create(organization=org, user=sender, role="EMPLOYEE")
    Membership.objects.create(organization=other, user=outsider, role="EMPLOYEE")
    client = APIClient()
    client.force_authenticate(sender)
    response = client.post("/api/v1/employees/messages/", {"recipient": outsider.id, "body": "should not send"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 400
    assert not DirectMessage.objects.filter(organization=org).exists()

@pytest.mark.django_db
def test_notification_read_is_recipient_and_tenant_scoped():
    User = get_user_model()
    recipient = User.objects.create_user(username="notice-owner", password="strong-password-123")
    other_user = User.objects.create_user(username="notice-outsider", password="strong-password-123")
    org = Organization.objects.create(name="Agency Five", slug="agency-five")
    other = Organization.objects.create(name="Agency Six", slug="agency-six")
    Membership.objects.create(organization=org, user=recipient, role="EMPLOYEE")
    Membership.objects.create(organization=org, user=other_user, role="EMPLOYEE")
    notice = Notification.objects.create(organization=org, recipient=recipient, title="Review needed")
    client = APIClient()
    client.force_authenticate(other_user)
    response = client.post(f"/api/v1/employees/notifications/{notice.id}/read/", {}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 404
    notice.refresh_from_db()
    assert notice.read_at is None

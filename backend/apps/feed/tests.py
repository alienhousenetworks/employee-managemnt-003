import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.organizations.models import Organization, Membership
from .models import FeedPost

@pytest.mark.django_db
def test_feed_is_tenant_scoped_and_persists():
    user = get_user_model().objects.create_user(username="member", password="strong-password-123")
    org = Organization.objects.create(name="North Agency", slug="north-agency")
    other = Organization.objects.create(name="South Agency", slug="south-agency")
    Membership.objects.create(organization=org, user=user, role="EMPLOYEE", department="Engineering")
    FeedPost.objects.create(organization=other, author=user, body="must not leak")
    client = APIClient(); client.force_authenticate(user)
    response = client.get("/api/v1/feed/posts/", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 200
    assert response.data["results"] == [] or response.data == []

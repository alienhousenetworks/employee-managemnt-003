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
    assert len(response.data) == 0

@pytest.mark.django_db
def test_department_post_is_not_visible_or_reactable_across_departments():
    User = get_user_model()
    author = User.objects.create_user(username="author-dept", password="strong-password-123")
    member = User.objects.create_user(username="member-dept", password="strong-password-123")
    org = Organization.objects.create(name="Dept Agency", slug="dept-agency")
    Membership.objects.create(organization=org, user=author, role="EMPLOYEE", department="Engineering")
    Membership.objects.create(organization=org, user=member, role="EMPLOYEE", department="Marketing")
    post = FeedPost.objects.create(organization=org, author=author, body="engineering only", visibility="DEPARTMENT", department="Engineering")
    client = APIClient()
    client.force_authenticate(member)
    response = client.post(f"/api/v1/feed/posts/{post.id}/reactions/", {"reaction": "LIKE"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 404

@pytest.mark.django_db
def test_reaction_type_is_validated():
    user = get_user_model().objects.create_user(username="reactor", password="strong-password-123")
    org = Organization.objects.create(name="Reaction Agency", slug="reaction-agency")
    Membership.objects.create(organization=org, user=user, role="EMPLOYEE", department="Design")
    post = FeedPost.objects.create(organization=org, author=user, body="hello")
    client = APIClient()
    client.force_authenticate(user)
    response = client.post(f"/api/v1/feed/posts/{post.id}/reactions/", {"reaction": "UNSAFE_VALUE"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 400

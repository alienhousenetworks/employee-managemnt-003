import hashlib
import hmac
import json
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.organizations.models import Organization, Membership
from .models import Project, Task, TaskDependency, ProjectDeliverable, GitHubRepositoryLink, GitHubWorkItemLink, GitHubWebhookDelivery

@pytest.mark.django_db
def test_task_dependency_rejects_cycles():
    user = get_user_model().objects.create_user(username="delivery-owner", password="strong-password-123")
    org = Organization.objects.create(name="Delivery Agency", slug="delivery-agency")
    Membership.objects.create(organization=org, user=user, role="MANAGER", department="Delivery")
    project = Project.objects.create(organization=org, name="Website", service_line="DEVELOPMENT")
    first = Task.objects.create(organization=org, project=project, title="Design", created_by=user)
    second = Task.objects.create(organization=org, project=project, title="Build", created_by=user)
    TaskDependency.objects.create(organization=org, predecessor=first, successor=second, created_by=user)
    client = APIClient()
    client.force_authenticate(user)
    response = client.post("/api/v1/delivery/task-dependencies/", {"predecessor": str(second.id), "successor": str(first.id)}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 400
    assert TaskDependency.objects.count() == 1

@pytest.mark.django_db
def test_deliverable_requires_qa_approval_before_delivery():
    user = get_user_model().objects.create_user(username="delivery-manager", password="strong-password-123")
    org = Organization.objects.create(name="QA Agency", slug="qa-agency")
    Membership.objects.create(organization=org, user=user, role="MANAGER", department="Engineering")
    project = Project.objects.create(organization=org, name="Release", service_line="DEVELOPMENT")
    item = ProjectDeliverable.objects.create(organization=org, project=project, title="Release candidate", created_by=user, status="IN_PROGRESS")
    client = APIClient()
    client.force_authenticate(user)
    early = client.post(f"/api/v1/delivery/deliverables/{item.id}/transition/", {"action": "deliver"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert early.status_code == 400
    submitted = client.post(f"/api/v1/delivery/deliverables/{item.id}/transition/", {"action": "submit_qa"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert submitted.status_code == 200
    approved = client.post(f"/api/v1/delivery/deliverables/{item.id}/transition/", {"action": "qa_pass", "note": "Acceptance criteria verified"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert approved.status_code == 200
    delivered = client.post(f"/api/v1/delivery/deliverables/{item.id}/transition/", {"action": "deliver"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert delivered.status_code == 200
    item.refresh_from_db()
    assert item.status == "DELIVERED"
    assert item.version == 4

@pytest.mark.django_db
def test_deliverable_cannot_reference_another_tenant_project():
    user = get_user_model().objects.create_user(username="delivery-member", password="strong-password-123")
    org = Organization.objects.create(name="Own Agency", slug="own-agency")
    other = Organization.objects.create(name="Other Agency", slug="other-agency")
    Membership.objects.create(organization=org, user=user, role="EMPLOYEE")
    project = Project.objects.create(organization=other, name="Foreign", service_line="AI")
    client = APIClient()
    client.force_authenticate(user)
    response = client.post("/api/v1/delivery/deliverables/", {"project": str(project.id), "title": "Should be blocked"}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 400
    assert not ProjectDeliverable.objects.filter(organization=org).exists()

@pytest.mark.django_db
def test_opportunity_rejects_foreign_tenant_client():
    user = get_user_model().objects.create_user(username="crm-manager", password="strong-password-123")
    org = Organization.objects.create(name="CRM Agency", slug="crm-agency")
    other = Organization.objects.create(name="Foreign CRM", slug="foreign-crm")
    Membership.objects.create(organization=org, user=user, role="SALES")
    foreign_client = __import__("apps.delivery.models", fromlist=["ClientAccount"]).ClientAccount.objects.create(organization=other, name="Foreign Client")
    client = APIClient()
    client.force_authenticate(user)
    response = client.post("/api/v1/delivery/opportunities/", {"client": str(foreign_client.id), "name": "Test opportunity", "service_line": "AI", "probability_percent": 25}, format="json", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 400

@pytest.mark.django_db
def test_service_template_is_organization_scoped():
    from .models import ServiceTemplate
    user = get_user_model().objects.create_user(username="template-manager", password="strong-password-123")
    org = Organization.objects.create(name="Template Agency", slug="template-agency")
    other = Organization.objects.create(name="Other Templates", slug="other-templates")
    Membership.objects.create(organization=org, user=user, role="MANAGER")
    ServiceTemplate.objects.create(organization=other, service_line="AI", name="Foreign template")
    client = APIClient()
    client.force_authenticate(user)
    response = client.get("/api/v1/delivery/service-templates/", HTTP_X_ORGANIZATION_ID=str(org.id))
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_project_rejects_foreign_tenant_manager_and_task_assignee():
    User = get_user_model()
    member = User.objects.create_user(username="delivery-local-member", password="strong-password-123")
    foreign = User.objects.create_user(username="delivery-foreign-member", password="strong-password-123")
    org = Organization.objects.create(name="Assignment Tenant", slug="assignment-tenant")
    other = Organization.objects.create(name="Foreign Assignment Tenant", slug="foreign-assignment-tenant")
    Membership.objects.create(organization=org, user=member, role="MANAGER")
    Membership.objects.create(organization=other, user=foreign, role="EMPLOYEE")
    client = APIClient()
    client.force_authenticate(member)
    project_response = client.post(
        "/api/v1/delivery/projects/",
        {"name": "Cross-tenant manager", "service_line": "SOFTWARE", "project_manager": str(foreign.id)},
        format="json", HTTP_X_ORGANIZATION_ID=str(org.id),
    )
    assert project_response.status_code == 400
    project = Project.objects.create(organization=org, name="Local project", service_line="SOFTWARE")
    task_response = client.post(
        "/api/v1/delivery/tasks/",
        {"project": str(project.id), "title": "Cross-tenant assignee", "assignee": str(foreign.id)},
        format="json", HTTP_X_ORGANIZATION_ID=str(org.id),
    )
    assert task_response.status_code == 400
    assert not Task.objects.filter(organization=org).exists()


@pytest.mark.django_db
def test_github_webhook_requires_signature_and_deduplicates_delivery(monkeypatch):
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "test-github-webhook-secret")
    user = get_user_model().objects.create_user(username="github-webhook-owner", password="strong-password-123")
    org = Organization.objects.create(name="Webhook Agency", slug="webhook-agency")
    Membership.objects.create(organization=org, user=user, role="MANAGER")
    project = Project.objects.create(organization=org, name="Webhook Project", service_line="SOFTWARE")
    task = Task.objects.create(organization=org, project=project, title="Implement issue 17", created_by=user)
    repository = GitHubRepositoryLink.objects.create(
        organization=org, project=project, repository_full_name="alienhousenetworks/example",
        repository_url="https://github.com/alienhousenetworks/example", installation_id="123", is_enabled=True,
    )
    GitHubWorkItemLink.objects.create(
        organization=org, task=task, repository=repository, external_id="17",
        item_type="issue", title="Old title", url="https://github.com/alienhousenetworks/example/issues/17", state="open",
    )
    payload = {
        "action": "closed",
        "installation": {"id": 123},
        "repository": {"full_name": "alienhousenetworks/example"},
        "issue": {"number": 17, "title": "Issue completed", "html_url": "https://github.com/alienhousenetworks/example/issues/17", "state": "closed"},
    }
    raw = json.dumps(payload, separators=(",", ":")).encode()
    signature = "sha256=" + hmac.new(b"test-github-webhook-secret", raw, hashlib.sha256).hexdigest()
    client = APIClient()
    headers = {
        "HTTP_X_HUB_SIGNATURE_256": signature,
        "HTTP_X_GITHUB_DELIVERY": "delivery-abc-123",
        "HTTP_X_GITHUB_EVENT": "issues",
    }
    invalid = client.post("/api/v1/delivery/github/webhook/", data=raw, content_type="application/json",
                          HTTP_X_HUB_SIGNATURE_256="sha256=invalid",
                          HTTP_X_GITHUB_DELIVERY="delivery-abc-123", HTTP_X_GITHUB_EVENT="issues")
    assert invalid.status_code == 403
    first = client.post("/api/v1/delivery/github/webhook/", data=raw, content_type="application/json", **headers)
    assert first.status_code == 200
    assert first.data["duplicate"] is False
    item.refresh_from_db()
    assert item.state == "closed"
    assert item.title == "Issue completed"
    duplicate = client.post("/api/v1/delivery/github/webhook/", data=raw, content_type="application/json", **headers)
    assert duplicate.status_code == 200
    assert duplicate.data["duplicate"] is True
    assert GitHubWebhookDelivery.objects.filter(organization=org, delivery_id="delivery-abc-123").count() == 1
    changed_payload = {**payload, "action": "reopened"}
    changed_raw = json.dumps(changed_payload, separators=(",", ":")).encode()
    changed_signature = "sha256=" + hmac.new(b"test-github-webhook-secret", changed_raw, hashlib.sha256).hexdigest()
    replay = client.post(
        "/api/v1/delivery/github/webhook/", data=changed_raw, content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=changed_signature, HTTP_X_GITHUB_DELIVERY="delivery-abc-123",
        HTTP_X_GITHUB_EVENT="issues",
    )
    assert replay.status_code == 409

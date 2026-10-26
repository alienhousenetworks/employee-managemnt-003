from rest_framework import serializers
from .models import ClientAccount, Project, Task

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAccount
        fields = ["id", "name", "status", "account_owner", "created_at"]
        read_only_fields = ["id", "created_at"]
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "client", "name", "service_line", "description", "status", "project_manager", "start_date", "due_date", "created_at"]
        read_only_fields = ["id", "created_at"]
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "project", "title", "description", "acceptance_criteria", "status", "priority", "assignee", "created_by", "due_date", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

from .models import TaskDependency, ProjectDeliverable

class TaskDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskDependency
        fields = ["id", "predecessor", "successor", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]

class ProjectDeliverableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDeliverable
        fields = ["id", "project", "title", "description", "acceptance_criteria", "status", "version", "evidence_url", "qa_notes", "created_by", "approved_by", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "version", "qa_notes", "created_by", "approved_by", "created_at", "updated_at"]

from .models import ServiceTemplate, Opportunity, ClientRenewal, GitHubRepositoryLink, GitHubWorkItemLink

class ServiceTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTemplate
        fields = ["id", "service_line", "name", "description", "default_tasks", "default_deliverables", "active", "created_at"]
        read_only_fields = ["id", "created_at"]

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = ["id", "client", "name", "source", "service_line", "stage", "estimated_value", "currency", "probability_percent", "next_action", "next_action_date", "owner", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
    def validate_probability_percent(self, value):
        if value > 100:
            raise serializers.ValidationError("Probability must be between 0 and 100.")
        return value

class ClientRenewalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientRenewal
        fields = ["id", "client", "project", "renewal_date", "contract_value", "status", "owner", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]

class GitHubRepositoryLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubRepositoryLink
        fields = ["id", "project", "repository_full_name", "repository_url", "installation_id", "is_enabled", "created_at"]
        read_only_fields = ["id", "created_at"]

class GitHubWorkItemLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitHubWorkItemLink
        fields = ["id", "task", "repository", "external_id", "item_type", "title", "url", "state", "synced_at", "created_at"]
        read_only_fields = ["id", "created_at"]

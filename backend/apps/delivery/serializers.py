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

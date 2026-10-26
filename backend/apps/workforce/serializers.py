from rest_framework import serializers
from .models import EmployeeProfile

class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ["id", "employee_code", "display_name", "job_title", "department", "manager", "business_phone", "skills", "is_active", "created_at"]
        read_only_fields = ["id", "created_at", "is_active", "manager"]

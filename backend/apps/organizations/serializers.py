from rest_framework import serializers
from .models import Organization, Membership

class MembershipSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source="organization.name", read_only=True)
    class Meta:
        model = Membership
        fields = ["id", "organization", "organization_name", "role", "department", "is_active"]

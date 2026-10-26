from rest_framework.permissions import BasePermission
from .models import Membership

class HasActiveOrganizationMembership(BasePermission):
    """Require an explicit active membership; never trust tenant IDs alone."""
    def has_permission(self, request, view):
        org_id = request.headers.get("X-Organization-ID") or request.query_params.get("organization_id")
        if not org_id or not request.user or not request.user.is_authenticated:
            return False
        membership = Membership.objects.filter(user=request.user, organization_id=org_id, is_active=True, organization__is_active=True).first()
        if not membership:
            return False
        request.organization = membership.organization
        request.membership = membership
        return True

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.organizations.models import Membership
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import EmployeeProfile, DirectMessage, Notification
from .serializers import EmployeeProfileSerializer, DirectMessageSerializer, NotificationSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        memberships = Membership.objects.filter(user=request.user, is_active=True, organization__is_active=True).select_related("organization")
        return Response({"id": str(request.user.pk), "username": request.user.get_username(), "email": request.user.email, "organizations": [{"id": str(m.organization_id), "name": m.organization.name, "role": m.role, "department": m.department} for m in memberships]})

class EmployeeDirectoryView(generics.ListAPIView):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        qs = EmployeeProfile.objects.filter(organization=self.request.organization, is_active=True).order_by("display_name")
        search = self.request.query_params.get("search", "").strip()
        department = self.request.query_params.get("department", "").strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(Q(display_name__icontains=search) | Q(employee_code__icontains=search) | Q(job_title__icontains=search))
        if department:
            qs = qs.filter(department=department)
        return qs

class DirectMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        return DirectMessage.objects.filter(organization=self.request.organization).filter(
            models_q(self.request.user)
        ).select_related("sender", "recipient")
    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError
        recipient_id = self.request.data.get("recipient")
        recipient_membership = Membership.objects.filter(
            organization=self.request.organization, user_id=recipient_id,
            is_active=True, organization__is_active=True
        ).first()
        if not recipient_membership:
            raise ValidationError({"recipient": "Recipient must be an active member of this organization."})
        serializer.save(organization=self.request.organization, sender=self.request.user, recipient=recipient_membership.user)

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def get_queryset(self):
        return Notification.objects.filter(organization=self.request.organization, recipient=self.request.user)

class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    def post(self, request, notification_id):
        notification = Notification.objects.filter(
            id=notification_id, organization=request.organization, recipient=request.user
        ).first()
        if not notification:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at"])
        return Response(NotificationSerializer(notification).data)

def models_q(user):
    from django.db.models import Q
    return Q(sender=user) | Q(recipient=user)

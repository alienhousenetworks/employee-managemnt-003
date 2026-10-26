from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Membership
from .serializers import MembershipSerializer

class MyOrganizationsView(ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Membership.objects.filter(user=self.request.user, is_active=True, organization__is_active=True).select_related("organization").order_by("organization__name")

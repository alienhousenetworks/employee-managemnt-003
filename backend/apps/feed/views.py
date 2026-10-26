from django.db.models import Q
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.organizations.permissions import HasActiveOrganizationMembership
from .models import FeedPost, FeedComment, FeedReaction
from .serializers import FeedPostSerializer, FeedCommentSerializer

def visible_posts(request):
    membership = request.membership
    return FeedPost.objects.filter(organization=request.organization).filter(
        Q(visibility=FeedPost.Visibility.ORGANIZATION)
        | Q(visibility=FeedPost.Visibility.DEPARTMENT, department=membership.department)
        | Q(visibility=FeedPost.Visibility.PRIVATE, author=request.user)
    )

class FeedView(generics.ListCreateAPIView):
    serializer_class = FeedPostSerializer
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]

    def get_queryset(self):
        qs = visible_posts(self.request).select_related("author").prefetch_related("comments", "reactions")
        project_id = self.request.query_params.get("project_id")
        if project_id:
            qs = qs.filter(linked_record_type="project", linked_record_id=project_id)
        return qs

    def perform_create(self, serializer):
        visibility = serializer.validated_data.get("visibility", FeedPost.Visibility.ORGANIZATION)
        if visibility == FeedPost.Visibility.DEPARTMENT and not self.request.membership.department:
            raise ValidationError({"visibility": "A department is required for department-only posts."})
        serializer.save(
            organization=self.request.organization,
            author=self.request.user,
            department=self.request.membership.department if visibility == FeedPost.Visibility.DEPARTMENT else "",
        )

class FeedCommentCreateView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]

    def post(self, request, post_id):
        post = visible_posts(request).filter(id=post_id).first()
        if not post:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FeedCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(post=post, author=request.user)
        return Response(FeedCommentSerializer(comment).data, status=status.HTTP_201_CREATED)

class FeedReactionView(APIView):
    permission_classes = [IsAuthenticated, HasActiveOrganizationMembership]
    ALLOWED_REACTIONS = {"LIKE", "CELEBRATE", "SUPPORT", "INSIGHTFUL", "THANKS"}

    def post(self, request, post_id):
        post = visible_posts(request).filter(id=post_id).first()
        if not post:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        reaction = str(request.data.get("reaction", "LIKE")).upper()
        if reaction not in self.ALLOWED_REACTIONS:
            raise ValidationError({"reaction": f"Choose one of: {', '.join(sorted(self.ALLOWED_REACTIONS))}."})
        obj, created = FeedReaction.objects.get_or_create(post=post, user=request.user, reaction=reaction)
        return Response({"id": str(obj.id), "reaction": obj.reaction, "created": created}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

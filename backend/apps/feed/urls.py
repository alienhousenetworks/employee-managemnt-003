from django.urls import path
from .views import FeedView, FeedCommentCreateView, FeedReactionView
urlpatterns = [path("posts/", FeedView.as_view(), name="feed-posts"), path("posts/<uuid:post_id>/comments/", FeedCommentCreateView.as_view(), name="feed-comments"), path("posts/<uuid:post_id>/reactions/", FeedReactionView.as_view(), name="feed-reactions")]

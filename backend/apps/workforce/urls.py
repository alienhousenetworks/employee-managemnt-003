from django.urls import path
from .views import EmployeeDirectoryView, DirectMessageListCreateView, NotificationListView, NotificationReadView

urlpatterns = [
    path("", EmployeeDirectoryView.as_view(), name="employee-directory"),
    path("messages/", DirectMessageListCreateView.as_view(), name="direct-messages"),
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path("notifications/<uuid:notification_id>/read/", NotificationReadView.as_view(), name="notification-read"),
]

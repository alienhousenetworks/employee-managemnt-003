from django.urls import path
from .views import WhatsAppWebhookView, WhatsAppContactListCreateView, WhatsAppMessageListCreateView, WhatsAppMessageApprovalView
urlpatterns = [
    path("webhook/", WhatsAppWebhookView.as_view(), name="whatsapp-webhook"),
    path("contacts/", WhatsAppContactListCreateView.as_view(), name="whatsapp-contacts"),
    path("messages/", WhatsAppMessageListCreateView.as_view(), name="whatsapp-messages"),
    path("messages/<uuid:message_id>/approve/", WhatsAppMessageApprovalView.as_view(), name="whatsapp-message-approve"),
]

from django.urls import path
from .views import WhatsAppWebhookView, WhatsAppContactListCreateView, WhatsAppMessageListCreateView, WhatsAppMessageApprovalView, WhatsAppConsentView
urlpatterns = [
    path("webhook/", WhatsAppWebhookView.as_view(), name="whatsapp-webhook"),
    path("contacts/", WhatsAppContactListCreateView.as_view(), name="whatsapp-contacts"),
    path("messages/", WhatsAppMessageListCreateView.as_view(), name="whatsapp-messages"),
    path("contacts/<uuid:contact_id>/consent/", WhatsAppConsentView.as_view(), name="whatsapp-consent"),
    path("messages/<uuid:message_id>/approve/", WhatsAppMessageApprovalView.as_view(), name="whatsapp-message-approve"),
]

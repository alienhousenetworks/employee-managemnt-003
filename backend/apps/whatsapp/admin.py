from django.contrib import admin
from .models import WhatsAppIntegration, WhatsAppContact, WhatsAppMessage

@admin.register(WhatsAppIntegration)
class WhatsAppIntegrationAdmin(admin.ModelAdmin):
    list_display = ("organization", "phone_number_id", "display_phone_number", "is_enabled")
    list_filter = ("is_enabled", "organization")
    search_fields = ("organization__name", "phone_number_id", "display_phone_number")

@admin.register(WhatsAppContact)
class WhatsAppContactAdmin(admin.ModelAdmin):
    list_display = ("organization", "phone_e164", "consent", "created_at")
    list_filter = ("organization", "consent")
    search_fields = ("phone_e164", "display_name")

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ("organization", "contact", "direction", "status", "created_at")
    list_filter = ("organization", "direction", "status")
    search_fields = ("provider_message_id", "contact__phone_e164", "body")
    readonly_fields = ("provider_message_id", "created_at", "updated_at")

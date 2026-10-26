from django.contrib import admin
from .models import Organization, Membership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    readonly_fields = ("id", "created_at")
    ordering = ("name",)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "role", "department", "is_active", "created_at")
    list_filter = ("organization", "role", "department", "is_active")
    search_fields = ("organization__name", "user__username", "user__email", "department")
    readonly_fields = ("id", "created_at")
    autocomplete_fields = ("organization", "user")

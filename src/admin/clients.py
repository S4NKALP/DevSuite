from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from src.admin.base import admin_site
from src.models.clients import Client


@admin.register(Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name_display",
        "short_code",
        "company_name",
        "email",
        "phone",
        "created_at",
        "updated_at",
    )
    list_display_links = ("name_display",)
    list_per_page = 25

    search_fields = ("name", "short_code", "email", "phone", "company_name")
    list_filter = ("created_at", "updated_at")
    ordering = ("name",)

    fieldsets = (
        (
            _("Basic Info"),
            {
                "fields": ("name", "short_code", "company_name"),
                "description": "Client’s identifying information. The short code is auto-generated if left blank.",
            },
        ),
        (
            _("Contact Details"),
            {
                "fields": ("email", "phone", "address"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),  # collapsible section for cleaner UI
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def name_display(self, obj):
        """Display name with subtle emphasis."""
        return format_html(
            "<strong>{}</strong><br><small style='color: #888;'>{}</small>",
            obj.name,
            obj.short_code or "—",
        )

    name_display.short_description = "Client"

    def save_model(self, request, obj, form, change):
        """
        Ensure short_code generation happens gracefully and show a message.
        """
        if not obj.short_code:
            generated = obj.generate_short_code()
            obj.short_code = generated
            self.message_user(
                request,
                f"Short code '{generated}' was automatically generated for client '{obj.name}'.",
            )
        super().save_model(request, obj, form, change)

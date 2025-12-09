from django.contrib import admin
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import SplitPhoneNumberField

from src.admin.shared import (
    admin_site,
    format_placeholder,
    format_strong_with_subtext,
)
from src.models.clients import Client


class ClientAdminForm(ModelForm):
    phone = SplitPhoneNumberField(required=True)

    class Meta:
        model = Client
        fields = "__all__"


@admin.register(Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    form = ClientAdminForm

    list_display = (
        "name_display",
        "short_code",
        "company_name",
        "email",
        "formatted_phone",
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
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def name_display(self, obj):
        """Display name with subtle emphasis."""
        return format_strong_with_subtext(obj.name, obj.short_code)

    name_display.short_description = "Client"

    def formatted_phone(self, obj):
        """Displays the phone number in International format on the list view."""
        if obj.phone:
            # Uses the .as_international property from the PhoneNumber wrapper
            return obj.phone.as_international
        return format_placeholder()

    formatted_phone.short_description = "Phone"

    def save_model(self, request, obj, form, change):
        # Check if the short_code was empty before this save operation
        short_code_was_empty = not obj.short_code

        # Call the parent save method, which calls obj.save() and triggers
        # the short_code generation logic you put in the model.
        super().save_model(request, obj, form, change)

        # Check if it was generated and display a message
        if short_code_was_empty and obj.short_code:
            self.message_user(
                request,
                f"Short code '{obj.short_code}' was automatically generated for client '{obj.name}'.",
            )

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from src.admin.base import admin_site
from src.models.services import Credential, Service


class CredentialInline(admin.TabularInline):
    model = Credential
    extra = 1
    fields = ("url", "username", "password", "notes")
    show_change_link = True
    verbose_name_plural = "Credentials"

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields["password"].widget.attrs["type"] = "password"
        return formset


@admin.register(Service, site=admin_site)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name_display",
        "client_display",
        "type_badge",
        "provider",
        "cost_display",
        "renewal_price_display",
        "expiry_display",
        "auto_renew_display",
    )
    list_filter = (
        "service_type",
        "auto_renew",
        "provider",
        "expiry_date",
        "client",
    )
    search_fields = ("name", "client__name", "provider")
    ordering = ("-created_at",)
    list_per_page = 25
    inlines = [CredentialInline]

    fieldsets = (
        (
            _("Service Info"),
            {
                "fields": ("client", "service_type", "name", "provider"),
            },
        ),
        (
            _("Billing"),
            {
                "fields": ("cost", "renewal_price", "auto_renew"),
            },
        ),
        (
            _("Duration"),
            {
                "fields": ("start_date", "expiry_date"),
                "description": "Start and expiry dates are used for renewal reminders.",
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
        return format_html("<strong>{}</strong>", obj.name)

    name_display.short_description = "Service"

    def client_display(self, obj):
        return obj.client.name

    client_display.short_description = "Client"

    def type_badge(self, obj):
        color_map = {
            "DOMAIN": "#007bff",
            "HOSTING": "#28a745",
            "VPS": "#6f42c1",
            "SSL": "#17a2b8",
            "OTHER": "#6c757d",
        }
        color = color_map.get(obj.service_type, "#333")
        return format_html(
            "<span style='background:{}; color:white; padding:3px 8px; border-radius:6px; font-size:12px;'>{}</span>",
            color,
            obj.get_service_type_display(),
        )

    type_badge.short_description = "Type"

    def cost_display(self, obj):
        return format_html("<b>${:,.2f}</b>", obj.cost)

    cost_display.short_description = "Cost"

    def renewal_price_display(self, obj):
        return format_html("<b>${:,.2f}</b>", obj.renewal_price)

    renewal_price_display.short_description = "Renewal"

    def expiry_display(self, obj):
        """Color-coded expiry indicator."""
        if not obj.expiry_date:
            return format_html("<span style='color:#888;'>—</span>")
        today = timezone.localdate()
        delta = (obj.expiry_date - today).days

        if delta < 0:
            color = "#dc3545"
            label = "Expired"
        elif delta <= 7:
            color = "#f39c12"
            label = f"Expiring ({delta}d)"
        else:
            color = "#28a745"
            label = f"In {delta}d"

        return format_html(
            "<span style='color:{}; font-weight:600;'>{}</span><br><small>{}</small>",
            color,
            label,
            obj.expiry_date,
        )

    expiry_display.short_description = "Expiry"

    def auto_renew_display(self, obj):
        icon = "✅" if obj.auto_renew else "❌"
        color = "#28a745" if obj.auto_renew else "#999"
        return format_html(
            f"<span style='color:{color}; font-size:14px;'>{icon}</span>"
        )

    auto_renew_display.short_description = "Auto Renew"

    def save_model(self, request, obj, form, change):
        if obj.start_date and obj.expiry_date and obj.expiry_date < obj.start_date:
            self.message_user(
                request,
                "⚠️ Expiry date cannot be earlier than start date.",
                level="warning",
            )
        elif obj.expiry_date and obj.expiry_date < timezone.localdate():
            self.message_user(
                request, "⚠️ Expiry date is already in the past.", level="warning"
            )
        super().save_model(request, obj, form, change)


@admin.register(Credential, site=admin_site)
class CredentialAdmin(admin.ModelAdmin):
    list_display = (
        "service_display",
        "username_display",
        "url_display",
        "notes_display",
    )
    list_filter = ("service__service_type", "service__client")
    search_fields = ("username", "service__name", "notes")
    ordering = ("service",)

    fieldsets = (
        (
            _("Credential Info"),
            {
                "fields": ("service", "url", "username", "password", "notes"),
            },
        ),
    )

    # --- DISPLAY HELPERS ---
    def service_display(self, obj):
        return format_html(
            "<strong>{}</strong><br><small>{}</small>",
            obj.service.name,
            obj.service.client.name,
        )

    service_display.short_description = "Service"

    def username_display(self, obj):
        return obj.username or format_html("<span style='color:#888;'>—</span>")

    username_display.short_description = "Username"

    def url_display(self, obj):
        if obj.url:
            return format_html("<a href='{}' target='_blank'>{}</a>", obj.url, obj.url)
        return format_html("<span style='color:#888;'>—</span>")

    url_display.short_description = "URL"

    def notes_display(self, obj):
        return (
            (obj.notes[:60] + "...")
            if obj.notes and len(obj.notes) > 60
            else (obj.notes or "—")
        )

    notes_display.short_description = "Notes"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("service", "service__client")

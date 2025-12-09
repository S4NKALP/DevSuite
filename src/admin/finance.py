from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from src.admin.shared import (
    admin_site,
    format_badge,
    format_currency,
    format_strong_with_subtext,
)
from src.models.finance import Expense, Invoice, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    fields = ("amount", "date", "method", "transaction_id")
    readonly_fields = ("transaction_id",)
    show_change_link = True
    verbose_name_plural = "Payments"


@admin.register(Invoice, site=admin_site)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number",
        "client_display",
        "project_display",
        "amount_display",
        "status_badge",
        "date_issued",
        "due_date",
    )
    list_display_links = ("invoice_number",)
    list_filter = ("status", "date_issued", "due_date")
    search_fields = (
        "invoice_number",
        "client__name",
        "client__short_code",
        "project__name",
    )
    ordering = ("-date_issued",)
    list_per_page = 25
    inlines = [PaymentInline]

    fieldsets = (
        (
            _("Invoice Details"),
            {
                "fields": (
                    "client",
                    "project",
                    "invoice_number",
                    "amount",
                    "status",
                ),
                "description": "Core invoice information. The <b>invoice number</b> is auto-generated upon creation.",
            },
        ),
        (
            _("Dates"),
            {
                "fields": ("date_issued", "due_date"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = (
        "invoice_number",
        "date_issued",
        "due_date",
        "created_at",
        "updated_at",
    )

    def client_display(self, obj):
        return format_strong_with_subtext(obj.client.name, obj.client.short_code)

    client_display.short_description = "Client"

    def project_display(self, obj):
        return obj.project.name

    project_display.short_description = "Project"

    def amount_display(self, obj):
        return format_currency(obj.amount)

    amount_display.short_description = "Amount"

    def status_badge(self, obj):
        color_map = {
            "DRAFT": "#999",
            "SENT": "#0066cc",
            "PAID": "#28a745",
            "OVERDUE": "#dc3545",
            "CANCELLED": "#6c757d",
        }
        color = color_map.get(obj.status, "#333")
        return format_badge(obj.get_status_display(), background=color)

    status_badge.short_description = "Status"

    def save_model(self, request, obj, form, change):
        if not obj.invoice_number:
            obj.save()  # triggers auto-generation
            self.message_user(
                request,
                f"Invoice number {obj.invoice_number} generated for {obj.client}.",
            )
        else:
            super().save_model(request, obj, form, change)


@admin.register(Expense, site=admin_site)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "category",
        "amount_display",
        "service",
        "date",
        "created_at",
    )
    list_filter = ("category", "date", "created_at")
    search_fields = ("description", "category", "service__name")
    ordering = ("-date",)

    fieldsets = (
        (
            _("Expense Info"),
            {
                "fields": ("service", "description", "category", "amount", "date"),
            },
        ),
        (
            _("Metadata"),
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("created_at",)

    def amount_display(self, obj):
        return format_currency(obj.amount)

    amount_display.short_description = "Amount"


@admin.register(Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_display",
        "amount_display",
        "date",
        "method",
        "transaction_id",
    )
    list_filter = ("method", "date")
    search_fields = ("invoice__invoice_number", "transaction_id", "method")
    ordering = ("-date",)

    fieldsets = (
        (
            _("Payment Info"),
            {
                "fields": ("invoice", "amount", "date", "method", "transaction_id"),
            },
        ),
    )

    def invoice_display(self, obj):
        return format_strong_with_subtext(
            obj.invoice.invoice_number, obj.invoice.client.name
        )

    invoice_display.short_description = "Invoice"

    def amount_display(self, obj):
        return format_currency(obj.amount)

    amount_display.short_description = "Amount"

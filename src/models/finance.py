from django.db import models

from src.models.base import TimeStampedModel
from src.models.clients import Client
from src.models.projects import Project
from src.models.services import Service


class Invoice(TimeStampedModel):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SENT", "Sent"),
        ("PAID", "Paid"),
        ("OVERDUE", "Overdue"),
        ("CANCELLED", "Cancelled"),
    ]
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="invoices"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="invoices"
    )
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_issued = models.DateField(auto_now_add=True)
    due_date = models.DateField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="DRAFT")

    def save(self, *args, **kwargs):
        if not self.id:
            client_code = self.client.short_code  # e.g., "NEX001"

            # Find last invoice for this client
            last_invoice = (
                Invoice.objects.filter(invoice_number__startswith=f"{client_code}-")
                .order_by("-invoice_number")
                .first()
            )

            if last_invoice:
                last_number = int(last_invoice.invoice_number.split("-")[1])
                new_number = last_number + 1
            else:
                new_number = 1

            # final format → NEX001-0001
            self.invoice_number = f"{client_code}-{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class Expense(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount}"


class Payment(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment of {self.amount} for {self.invoice}"

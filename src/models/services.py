from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from src.models.base import TimeStampedModel
from src.models.clients import Client


class Service(TimeStampedModel):
    TYPE_CHOICES = [
        ("DOMAIN", "Domain"),
        ("HOSTING", "Hosting"),
        ("VPS", "VPS"),
        ("SSL", "SSL"),
        ("OTHER", "Other"),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="services"
    )
    service_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(
        max_length=255, help_text="e.g. example.com or VPS - 4GB", db_index=True
    )
    provider = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    renewal_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    start_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["service_type"]),
            models.Index(fields=["client"]),
            models.Index(fields=["expiry_date"]),
        ]

    def clean(self):
        # ensure expiry_date is not earlier than start_date
        if self.start_date and self.expiry_date and self.expiry_date < self.start_date:
            raise ValidationError("Expiry date cannot be earlier than start date.")

        # optional: prevent expiry date in the past for new services
        today = timezone.localdate()
        if self.expiry_date and self.expiry_date < today:
            raise ValidationError("Expiry date cannot be in the past.")

    def __str__(self):
        return f"{self.get_service_type_display()} – {self.name}"


class Credential(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="credentials"
    )
    url = models.URLField(blank=True)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["service"]
        indexes = [
            models.Index(fields=["service"]),
        ]

    def __str__(self):
        # Avoid showing passwords / sensitive info
        cred_name = self.username or "No Username"
        return f"Credential ({cred_name}) for {self.service.name}"

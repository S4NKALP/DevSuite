from django.core.exceptions import ValidationError
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from src.models.base import TimeStampedModel


class Client(TimeStampedModel):
    name = models.CharField(max_length=255, db_index=True)
    short_code = models.CharField(max_length=6, unique=True, blank=True)
    email = models.EmailField()
    phone = PhoneNumberField(region="NP")
    address = models.TextField()
    company_name = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["short_code"]),
        ]

    def clean(self):
        # Optional validation for short_code length
        if self.short_code and len(self.short_code) > 6:
            raise ValidationError("Short code cannot be more than 6 characters.")

    def generate_short_code(self):
        """
        Generates a unique 6-character code:
        First 3 letters of name + incremental counter.
        Example: SAN001, SAN002, etc.
        Ensures uniqueness even if multiple clients share the same prefix.
        """
        base = self.name[:3].upper()

        # Find existing codes with same prefix
        existing = Client.objects.filter(short_code__startswith=base).values_list(
            "short_code", flat=True
        )

        # Extract available next number
        numbers = []
        for code in existing:
            try:
                number = int(code[3:])
                numbers.append(number)
            except (ValueError, IndexError):
                continue

        next_num = max(numbers, default=0) + 1
        return f"{base}{next_num:03d}"

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.short_code})"

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from src.models.base import TimeStampedModel
from src.models.clients import Client


class Project(TimeStampedModel):
    STATUS_CHOICES = [
        ("PLANNING", "Planning"),
        ("IN_PROGRESS", "In Progress"),
        ("ON_HOLD", "On Hold"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLANNING")
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["client"]),
        ]

    def clean(self):
        if self.start_date and self.deadline and self.deadline < self.start_date:
            raise ValidationError("Deadline cannot be earlier than start date.")

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class Milestone(TimeStampedModel):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="milestones"
    )
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["due_date"]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        status = "✓" if self.is_completed else "✗"
        return f"{self.title} [{status}]"


class Task(TimeStampedModel):
    STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("IN_PROGRESS", "In Progress"),
        ("REVIEW", "Review"),
        ("DONE", "Done"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="TODO")
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["status", "due_date"]
        indexes = [
            models.Index(fields=["project"]),
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]

    def clean(self):
        today = timezone.localdate()

        # Ensure due_date is not in the past
        if self.due_date and self.due_date < today:
            raise ValidationError("Due date cannot be in the past.")

    def __str__(self):
        return f"{self.title} — {self.get_status_display()}"

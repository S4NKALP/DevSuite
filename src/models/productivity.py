from django.core.exceptions import ValidationError
from django.db import models

from src.models.projects import Project, Task


class Note(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title[:50]  # avoid super long titles


class TimeEntry(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
    )
    description = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["start_time"]),
            models.Index(fields=["end_time"]),
            models.Index(fields=["project"]),
            models.Index(fields=["task"]),
        ]

    def clean(self):
        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError("End time cannot be earlier than start time.")

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
        else:
            self.duration = None

        super().save(*args, **kwargs)

    def __str__(self):
        duration_str = (
            str(self.duration).split(".")[0] if self.duration else "In Progress"
        )
        return f"{self.description} — {duration_str}"

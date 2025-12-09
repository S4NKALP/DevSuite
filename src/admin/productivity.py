from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from src.admin.base import admin_site
from src.models.productivity import Note, TimeEntry


@admin.register(Note, site=admin_site)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title_display", "created_at", "updated_at")
    search_fields = ("title", "content")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        (
            _("Note Details"),
            {
                "fields": ("title", "content"),
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

    def title_display(self, obj):
        """Show truncated title for clarity."""
        return format_html("<strong>{}</strong>", obj.title[:60])

    title_display.short_description = "Title"


@admin.register(TimeEntry, site=admin_site)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = (
        "description_display",
        "project_display",
        "task_display",
        "start_time_display",
        "end_time_display",
        "duration_display",
    )
    list_filter = (
        ("project", admin.RelatedOnlyFieldListFilter),
        ("task", admin.RelatedOnlyFieldListFilter),
        "start_time",
        "end_time",
    )
    search_fields = ("description", "project__name", "task__name")
    ordering = ("-start_time",)
    list_per_page = 25

    fieldsets = (
        (
            _("Work Details"),
            {
                "fields": ("project", "task", "description"),
            },
        ),
        (
            _("Timing"),
            {
                "fields": ("start_time", "end_time", "duration"),
                "description": "Duration is automatically calculated when both start and end times are provided.",
            },
        ),
    )
    readonly_fields = ("duration",)

    def description_display(self, obj):
        return format_html("<strong>{}</strong>", obj.description[:50])

    description_display.short_description = "Description"

    def project_display(self, obj):
        return obj.project.name if obj.project else "—"

    project_display.short_description = "Project"

    def task_display(self, obj):
        return obj.task.name if obj.task else "—"

    task_display.short_description = "Task"

    def start_time_display(self, obj):
        return (
            localtime(obj.start_time).strftime("%Y-%m-%d %H:%M")
            if obj.start_time
            else "—"
        )

    start_time_display.short_description = "Start"

    def end_time_display(self, obj):
        if obj.end_time:
            return localtime(obj.end_time).strftime("%Y-%m-%d %H:%M")
        return format_html("<span style='color: #999;'>In Progress</span>")

    end_time_display.short_description = "End"

    def duration_display(self, obj):
        if obj.duration:
            hours = obj.duration.total_seconds() / 3600
            color = "#28a745" if hours < 8 else "#f39c12"
            return format_html(
                "<span style='color: {}; font-weight: 600;'>{:.2f} hrs</span>",
                color,
                hours,
            )
        return format_html("<span style='color: #888;'>—</span>")

    duration_display.short_description = "Duration"

    def save_model(self, request, obj, form, change):
        obj.save()  # triggers auto duration calculation
        if obj.duration:
            hours = round(obj.duration.total_seconds() / 3600, 2)
            self.message_user(
                request, f"Duration automatically calculated: {hours} hours."
            )
        else:
            self.message_user(
                request, "Duration not calculated (in progress or missing end time)."
            )

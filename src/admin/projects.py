from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from src.admin.shared import (
    admin_site,
    format_badge,
    format_currency,
    format_placeholder,
    format_strong,
)
from src.models.projects import Milestone, Project, Task


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1
    fields = ("title", "due_date", "is_completed")
    show_change_link = True
    ordering = ("due_date",)
    verbose_name_plural = "Milestones"


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ("title", "status", "due_date")
    show_change_link = True
    ordering = ("status", "due_date")
    verbose_name_plural = "Tasks"


@admin.register(Project, site=admin_site)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name_display",
        "client_display",
        "status_badge",
        "start_date",
        "deadline",
        "budget_display",
    )
    list_filter = ("status", "client", "start_date", "deadline")
    search_fields = ("name", "client__name", "description")
    ordering = ("-created_at",)
    list_per_page = 25
    inlines = [MilestoneInline, TaskInline]

    fieldsets = (
        (
            _("Project Overview"),
            {
                "fields": ("client", "name", "description", "status"),
            },
        ),
        (
            _("Timeline"),
            {
                "fields": ("start_date", "deadline"),
                "description": "Start and deadline dates help in tracking project progress.",
            },
        ),
        (
            _("Financials"),
            {
                "fields": ("budget",),
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
        return format_strong(obj.name)

    name_display.short_description = "Project"

    def client_display(self, obj):
        return obj.client.name

    client_display.short_description = "Client"

    def status_badge(self, obj):
        color_map = {
            "PLANNING": "#6c757d",
            "IN_PROGRESS": "#007bff",
            "ON_HOLD": "#ffc107",
            "COMPLETED": "#28a745",
            "CANCELLED": "#dc3545",
        }
        color = color_map.get(obj.status, "#999")
        return format_badge(obj.get_status_display(), background=color)

    status_badge.short_description = "Status"

    def budget_display(self, obj):
        return format_currency(obj.budget) if obj.budget else format_placeholder()

    budget_display.short_description = "Budget"

    def save_model(self, request, obj, form, change):
        if obj.deadline and obj.start_date and obj.deadline < obj.start_date:
            self.message_user(
                request,
                "⚠️ Deadline cannot be earlier than start date.",
                level="warning",
            )
        super().save_model(request, obj, form, change)


@admin.register(Milestone, site=admin_site)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("title_display", "project_display", "due_date", "status_badge")
    list_filter = ("is_completed", "due_date", "project")
    search_fields = ("title", "project__name")
    ordering = ("due_date",)

    fieldsets = (
        (
            _("Milestone Info"),
            {
                "fields": ("project", "title", "due_date", "is_completed"),
            },
        ),
    )

    def title_display(self, obj):
        return format_strong(obj.title)

    title_display.short_description = "Title"

    def project_display(self, obj):
        return obj.project.name

    project_display.short_description = "Project"

    def status_badge(self, obj):
        color = "#28a745" if obj.is_completed else "#dc3545"
        text = "Completed" if obj.is_completed else "Pending"
        return format_badge(text, background=color)

    status_badge.short_description = "Status"


@admin.register(Task, site=admin_site)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title_display",
        "project_display",
        "status_badge",
        "due_date_display",
    )
    list_filter = ("status", "due_date", "project")
    search_fields = ("title", "project__name", "description")
    ordering = ("status", "due_date")

    fieldsets = (
        (
            _("Task Info"),
            {
                "fields": ("project", "title", "description", "status"),
            },
        ),
        (
            _("Schedule"),
            {
                "fields": ("due_date",),
                "description": "Due date cannot be in the past.",
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
        return format_strong(obj.title)

    title_display.short_description = "Title"

    def project_display(self, obj):
        return obj.project.name

    project_display.short_description = "Project"

    def due_date_display(self, obj):
        if not obj.due_date:
            return format_placeholder(None, "No due date", "#999")
        if obj.due_date < timezone.localdate():
            return format_badge(obj.due_date, background="#dc3545")
        if obj.due_date == timezone.localdate():
            return format_badge("Today", background="#f39c12")
        return obj.due_date

    due_date_display.short_description = "Due Date"

    def status_badge(self, obj):
        color_map = {
            "TODO": "#6c757d",
            "IN_PROGRESS": "#007bff",
            "REVIEW": "#ffc107",
            "DONE": "#28a745",
        }
        color = color_map.get(obj.status, "#333")
        return format_badge(obj.get_status_display(), background=color)

    status_badge.short_description = "Status"

    def save_model(self, request, obj, form, change):
        if obj.due_date and obj.due_date < timezone.localdate():
            self.message_user(
                request, "⚠️ Due date cannot be in the past.", level="warning"
            )
        super().save_model(request, obj, form, change)

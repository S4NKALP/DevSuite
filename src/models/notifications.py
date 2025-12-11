from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from src.models.base import TimeStampedModel
from src.models.finance import Invoice
from src.models.productivity import TimeEntry
from src.models.projects import Milestone, Project, Task
from src.models.services import Service

User = get_user_model()


class Notification(TimeStampedModel):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SENT", "Sent"),
        ("FAILED", "Failed"),
    ]

    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    sent_at = models.DateTimeField(null=True, blank=True)

    # Generic relation to link to the source object (Project, Invoice, etc.)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification to {self.recipient}: {self.subject}"

    def send(self):
        try:
            send_mail(
                self.subject,
                self.message,
                settings.DEFAULT_FROM_EMAIL,
                [self.recipient],
                fail_silently=False,
            )
            self.status = "SENT"
            self.sent_at = timezone.now()
        except Exception as e:
            self.status = "FAILED"
            # In a real app, we might want to log the error 'e'
            print(f"Failed to send email: {e}")
        self.save()


def get_admin_emails():
    """Return a list of admin emails."""
    # First try settings.ADMINS
    admins = getattr(settings, "ADMINS", [])
    if admins:
        return [email for name, email in admins]

    # Fallback to superusers
    return list(User.objects.filter(is_superuser=True).values_list("email", flat=True))


def create_and_send(recipient, subject, message, obj=None):
    """Helper to create and send a notification."""
    # Avoid duplicate notifications for the same event on the same day
    if obj:
        ct = ContentType.objects.get_for_model(obj)
        already_sent = Notification.objects.filter(
            recipient=recipient,
            subject=subject,
            content_type=ct,
            object_id=obj.id,
            created_at__date=timezone.localdate(),
        ).exists()
        if already_sent:
            return

    notification = Notification(
        recipient=recipient,
        subject=subject,
        message=message,
        content_type=ContentType.objects.get_for_model(obj) if obj else None,
        object_id=obj.id if obj else None,
    )
    notification.save()
    notification.send()


def check_and_send_notifications():
    """
    Checks for upcoming deadlines/due dates and sends notifications.
    Should be called periodically (e.g., via a cron job or Celery beat).
    """
    today = timezone.localdate()
    tomorrow = today + timezone.timedelta(days=1)

    admin_emails = get_admin_emails()
    if not admin_emails:
        print("Warning: No admin emails found.")

    # --- Projects (Deadline) ---
    # Notify Client & Admin if deadline is tomorrow
    projects_due = Project.objects.filter(deadline=tomorrow)
    for project in projects_due:
        # Notify Client
        if project.client.email:
            create_and_send(
                recipient=project.client.email,
                subject=f"Project Deadline Reminder: {project.name}",
                message=f"Dear {project.client.name},\n\nThe project '{project.name}' is due on {project.deadline}.\n\nRegards,\nDevSuite",
                obj=project,
            )

        # Notify Admin
        for email in admin_emails:
            create_and_send(
                recipient=email,
                subject=f"Admin Alert: Project Deadline - {project.name}",
                message=f"Project '{project.name}' for client {project.client.name} is due on {project.deadline}.",
                obj=project,
            )

    # --- Milestones (Due Date) ---
    # Notify Client & Admin if due_date is tomorrow
    milestones_due = Milestone.objects.filter(due_date=tomorrow, is_completed=False)
    for milestone in milestones_due:
        project = milestone.project
        # Notify Client
        if project.client.email:
            create_and_send(
                recipient=project.client.email,
                subject=f"Milestone Due: {milestone.title}",
                message=f"Dear {project.client.name},\n\nThe milestone '{milestone.title}' for project '{project.name}' is due on {milestone.due_date}.\n\nRegards,\nDevSuite",
                obj=milestone,
            )

        # Notify Admin
        for email in admin_emails:
            create_and_send(
                recipient=email,
                subject=f"Admin Alert: Milestone Due - {milestone.title}",
                message=f"Milestone '{milestone.title}' (Project: {project.name}) is due on {milestone.due_date}.",
                obj=milestone,
            )

    # --- Tasks (Due Date) ---
    # Notify Admin only
    tasks_due = Task.objects.filter(due_date=tomorrow).exclude(status="DONE")
    for task in tasks_due:
        for email in admin_emails:
            create_and_send(
                recipient=email,
                subject=f"Task Due: {task.title}",
                message=f"Task '{task.title}' (Project: {task.project.name}) is due on {task.due_date}.",
                obj=task,
            )

    # --- Services (Expiry Date) ---
    # Notify Client
    services_expiring = Service.objects.filter(expiry_date=tomorrow)
    for service in services_expiring:
        if service.client.email:
            create_and_send(
                recipient=service.client.email,
                subject=f"Service Expiry Warning: {service.name}",
                message=f"Dear {service.client.name},\n\nYour service '{service.name}' ({service.get_service_type_display()}) expires on {service.expiry_date}.\nPlease renew it soon.\n\nRegards,\nDevSuite",
                obj=service,
            )

    # --- Invoices (Due Date) ---
    # Notify Client
    invoices_due = Invoice.objects.filter(
        due_date=tomorrow, status__in=["SENT", "OVERDUE"]
    )
    for invoice in invoices_due:
        if invoice.client.email:
            create_and_send(
                recipient=invoice.client.email,
                subject=f"Invoice Due: {invoice.invoice_number}",
                message=f"Dear {invoice.client.name},\n\nInvoice {invoice.invoice_number} for {invoice.amount} is due on {invoice.due_date}.\nPlease make payment.\n\nRegards,\nDevSuite",
                obj=invoice,
            )

    # --- Productivity / TimeEntries ---
    # Notify Admin for recently completed time entries (last 24h)
    recent_entries = TimeEntry.objects.filter(
        end_time__gte=timezone.now() - timezone.timedelta(hours=24),
        end_time__lte=timezone.now(),
    )

    for entry in recent_entries:
        # Check if we already sent a notification for this entry
        if Notification.objects.filter(
            content_type=ContentType.objects.get_for_model(entry), object_id=entry.id
        ).exists():
            continue

        for email in admin_emails:
            create_and_send(
                recipient=email,
                subject=f"Time Entry Logged: {entry.description}",
                message=f"User logged time for '{entry.description}'.\nDuration: {entry.duration}\nEnd Time: {entry.end_time}",
                obj=entry,
            )

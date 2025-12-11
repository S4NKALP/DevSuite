from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from src.models.clients import Client
from src.models.finance import Invoice
from src.models.notifications import Notification, check_and_send_notifications
from src.models.productivity import TimeEntry
from src.models.projects import Milestone, Project, Task
from src.models.services import Service

User = get_user_model()


class NotificationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            "admin", "admin@example.com", "password"
        )
        self.client = Client.objects.create(
            name="Test Client", email="client@example.com"
        )
        self.tomorrow = timezone.localdate() + timedelta(days=1)

    def test_project_deadline_notification(self):
        with self.settings(ADMINS=[("Admin", "admin@example.com")]):
            Project.objects.create(
                name="Test Project", client=self.client, deadline=self.tomorrow
            )
            check_and_send_notifications()

            # 1 to client, 1 to admin
            self.assertEqual(len(mail.outbox), 2)
            self.assertTrue(
                Notification.objects.filter(
                    subject__contains="Project Deadline"
                ).exists()
            )

    def test_milestone_due_notification(self):
        with self.settings(ADMINS=[("Admin", "admin@example.com")]):
            project = Project.objects.create(name="Test Project", client=self.client)
            Milestone.objects.create(
                project=project, title="Test Milestone", due_date=self.tomorrow
            )
            check_and_send_notifications()

            # 1 to client, 1 to admin
            self.assertEqual(len(mail.outbox), 2)
            self.assertTrue(
                Notification.objects.filter(subject__contains="Milestone Due").exists()
            )

    def test_task_due_notification(self):
        with self.settings(ADMINS=[("Admin", "admin@example.com")]):
            project = Project.objects.create(name="Test Project", client=self.client)
            Task.objects.create(
                project=project, title="Test Task", due_date=self.tomorrow
            )
            check_and_send_notifications()

            # 1 to admin only
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, ["admin@example.com"])
            self.assertTrue(
                Notification.objects.filter(subject__contains="Task Due").exists()
            )

    def test_service_expiry_notification(self):
        Service.objects.create(
            client=self.client,
            name="Test Service",
            service_type="DOMAIN",
            expiry_date=self.tomorrow,
        )
        check_and_send_notifications()

        # 1 to client only
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["client@example.com"])
        self.assertTrue(
            Notification.objects.filter(subject__contains="Service Expiry").exists()
        )

    def test_invoice_due_notification(self):
        project = Project.objects.create(name="Test Project", client=self.client)
        Invoice.objects.create(
            client=self.client,
            project=project,
            amount=Decimal("100.00"),
            due_date=self.tomorrow,
            status="SENT",
        )
        check_and_send_notifications()

        # 1 to client
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["client@example.com"])
        self.assertTrue(
            Notification.objects.filter(subject__contains="Invoice Due").exists()
        )

    def test_time_entry_notification(self):
        with self.settings(ADMINS=[("Admin", "admin@example.com")]):
            project = Project.objects.create(name="Test Project", client=self.client)
            now = timezone.now()
            TimeEntry.objects.create(
                project=project,
                description="Work done",
                start_time=now - timedelta(hours=2),
                end_time=now - timedelta(hours=1),
            )
            check_and_send_notifications()

            # 1 to admin
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, ["admin@example.com"])
            self.assertTrue(
                Notification.objects.filter(
                    subject__contains="Time Entry Logged"
                ).exists()
            )

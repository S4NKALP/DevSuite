from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from src.models.clients import Client
from src.models.notifications import Notification, check_and_send_notifications
from src.models.projects import Project

User = get_user_model()


class NotificationTests(TestCase):
    def test_send_deadline_notifications(self):
        # Setup
        User.objects.create_superuser("admin", "admin@example.com", "password")
        client = Client.objects.create(name="Test Client", email="client@example.com")

        # Project due tomorrow
        tomorrow = timezone.localdate() + timezone.timedelta(days=1)
        Project.objects.create(name="Test Project", client=client, deadline=tomorrow)

        # Run notification check
        check_and_send_notifications()

        # Verify emails sent
        # Expecting 2 emails: 1 to client, 1 to admin
        self.assertEqual(len(mail.outbox), 2)

        # Verify Notification objects created
        self.assertEqual(Notification.objects.count(), 2)

        client_notif = Notification.objects.get(recipient="client@example.com")
        self.assertIn("Project Deadline Reminder", client_notif.subject)

        admin_notif = Notification.objects.get(recipient="admin@example.com")
        self.assertIn("Admin Alert", admin_notif.subject)

    def test_no_notifications_if_not_due(self):
        # Setup
        client = Client.objects.create(name="Test Client", email="client@example.com")

        # Project due day after tomorrow
        day_after = timezone.localdate() + timezone.timedelta(days=2)
        Project.objects.create(name="Future Project", client=client, deadline=day_after)

        check_and_send_notifications()

        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notification.objects.count(), 0)

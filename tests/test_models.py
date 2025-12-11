from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from src.models.clients import Client
from src.models.finance import Invoice
from src.models.productivity import TimeEntry
from src.models.projects import Milestone, Project, Task
from src.models.services import Service


class ClientModelTest(TestCase):
    def test_short_code_generation(self):
        client1 = Client.objects.create(name="Sankalp Corp", email="s@example.com")
        self.assertEqual(client1.short_code, "SAN001")

        client2 = Client.objects.create(name="Sankalp Inc", email="s2@example.com")
        self.assertEqual(client2.short_code, "SAN002")

        client3 = Client.objects.create(name="Other Corp", email="o@example.com")
        self.assertEqual(client3.short_code, "OTH001")


class ProjectModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(name="Test Client", email="c@example.com")

    def test_deadline_validation(self):
        start_date = timezone.localdate()
        deadline = start_date - timedelta(days=1)  # Deadline before start

        project = Project(
            name="Bad Project",
            client=self.client,
            start_date=start_date,
            deadline=deadline,
        )
        with self.assertRaises(ValidationError):
            project.clean()

    def test_milestone_str(self):
        project = Project.objects.create(name="P1", client=self.client)
        milestone = Milestone.objects.create(project=project, title="M1")
        self.assertIn("✗", str(milestone))

        milestone.is_completed = True
        milestone.save()
        self.assertIn("✓", str(milestone))

    def test_task_due_date_validation(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        task = Task(
            project=Project.objects.create(name="P1", client=self.client),
            title="Old Task",
            due_date=yesterday,
        )
        with self.assertRaises(ValidationError):
            task.clean()


class ServiceModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(name="Test Client", email="c@example.com")

    def test_expiry_date_validation(self):
        start_date = timezone.localdate()
        expiry_date = start_date - timedelta(days=1)

        service = Service(
            client=self.client,
            name="Bad Service",
            service_type="DOMAIN",
            start_date=start_date,
            expiry_date=expiry_date,
        )
        with self.assertRaises(ValidationError):
            service.clean()


class FinanceModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(name="Test Client", email="c@example.com")
        self.project = Project.objects.create(name="P1", client=self.client)

    def test_invoice_number_generation(self):
        # Client short code is TES001
        inv1 = Invoice.objects.create(
            client=self.client,
            project=self.project,
            amount=Decimal("100.00"),
            due_date=timezone.localdate(),
        )
        self.assertEqual(inv1.invoice_number, "TES001-0001")

        inv2 = Invoice.objects.create(
            client=self.client,
            project=self.project,
            amount=Decimal("200.00"),
            due_date=timezone.localdate(),
        )
        self.assertEqual(inv2.invoice_number, "TES001-0002")


class ProductivityModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(name="Test Client", email="c@example.com")
        self.project = Project.objects.create(name="P1", client=self.client)

    def test_duration_calculation(self):
        start = timezone.now()
        end = start + timedelta(hours=2, minutes=30)

        entry = TimeEntry.objects.create(
            project=self.project, description="Coding", start_time=start, end_time=end
        )

        # Refresh to get DB value if needed, but save() sets it on instance
        self.assertEqual(entry.duration, timedelta(hours=2, minutes=30))

    def test_clean_validation(self):
        start = timezone.now()
        end = start - timedelta(hours=1)

        entry = TimeEntry(
            project=self.project,
            description="Time Travel",
            start_time=start,
            end_time=end,
        )
        with self.assertRaises(ValidationError):
            entry.clean()

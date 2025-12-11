from django.core.management.base import BaseCommand

from src.models.notifications import check_and_send_notifications


class Command(BaseCommand):
    help = "Checks for upcoming deadlines and sends notifications."

    def handle(self, *args, **options):
        self.stdout.write("Checking for notifications...")
        check_and_send_notifications()
        self.stdout.write(self.style.SUCCESS("Successfully sent notifications."))

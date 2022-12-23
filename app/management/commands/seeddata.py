from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from app import models

class Command(BaseCommand):
    help = "Seed database"

    def handle(self, *args, **options):
        try:
            models.User.objects.create_superuser("admin", "admin@example.com", "password")
        except IntegrityError:
            pass

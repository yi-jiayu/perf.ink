from django.core.management.base import BaseCommand

from app import models, services


class Command(BaseCommand):
    help = "Load shift details for shifts missing details"

    def handle(self, *args, **options):
        for summary in models.SalmonRunShiftSummary.objects.filter(
            detail__isnull=True
        ).iterator():
            raw_detail = models.SalmonRunShiftDetailRaw.objects.get(
                uploaded_by=summary.uploaded_by, shift_id=summary.splatnet_id
            )
            services.update_shift_with_details(summary, raw_detail.data)
            self.stdout.write(".", ending="")
            self.stdout.flush()
        self.stdout.write("")

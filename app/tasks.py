import httpx
import structlog
from celery import shared_task
from django.db import transaction

from . import models, services

logger = structlog.get_logger(__name__)


@shared_task(autoretry_for=(httpx.ReadTimeout,), retry_backoff=True)
@transaction.atomic
def sync_salmon_run_shift_details(user_id: int, shift_ids: list[str]) -> None:
    log = logger.bind(user_id=user_id)
    log.info("syncing shift details", count=len(shift_ids))
    user = models.User.objects.get(pk=user_id)
    summaries = (
        models.SalmonRunShiftSummaryRaw.objects.select_for_update()
        .filter(uploaded_by=user_id, shift_id__in=shift_ids)
        .prefetch_related("detail")
    )
    for summary in summaries:
        if hasattr(summary, "detail"):
            log.info(
                "skipping already-synced shift detail",
                user_id=user_id,
                shift_id=summary.shift_id,
            )
            continue
        data = services.get_salmon_run_shift_detail(user, summary.shift_id)
        models.SalmonRunShiftDetailRaw.objects.create(
            summary=summary,
            shift_id=summary.shift_id,
            uploaded_by=user,
            data=data,
        )
        log.info("synced shift detail", shift_id=summary.shift_id)
    log.info("synced shift details", count=len(shift_ids))

import httpx
import structlog
from celery import shared_task
from django.db import transaction

from . import models, services

logger = structlog.get_logger(__name__)


@shared_task(autoretry_for=(httpx.ReadTimeout,), retry_backoff=True)
@transaction.atomic
def sync_salmon_run_shift_details(user_id: int, shift_ids: list[str]) -> None:
    user = models.User.objects.get(pk=user_id)
    summaries = (
        models.SalmonRunShiftSummaryRaw.objects.select_for_update(of=("self",))
        .filter(uploaded_by=user_id, shift_id__in=shift_ids)
        .select_related("detail")
    )
    for summary in summaries:
        if hasattr(summary, "detail"):
            logger.info(
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
        logger.info("synced shift detail", user_id=user_id, shift_id=summary.shift_id)

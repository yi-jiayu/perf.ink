import structlog
from celery import shared_task

from . import models, services

logger = structlog.get_logger(__name__)


@shared_task(autoretry_for=(TimeoutError,), retry_backoff=True)
def sync_salmon_run_shift_details(user_id: int, summary_ids: list[int]) -> None:
    user = models.User.objects.get(pk=user_id)
    summaries = models.SalmonRunShiftSummaryRaw.objects.filter(pk__in=summary_ids).only(
        "shift_id"
    )
    logger.info("syncing shift details", user_id=user.id, count=len(summaries))
    for summary in summaries:
        detail = services.sync_salmon_run_shift_detail(user, summary)
        logger.info("synced shift detail", user_id=user.id, shift_id=detail.shift_id)
    logger.info("synced shift details", user_id=user.id, count=len(summaries))

from typing import Callable, Concatenate, ParamSpec, TypeVar

import httpx
import structlog
from django.db import transaction

import splatnet

from . import models

logger = structlog.get_logger()


def get_splatnet_session(user: models.User) -> models.SplatnetSession:
    try:
        return models.SplatnetSession.objects.get(user=user)
    except models.SplatnetSession.DoesNotExist:
        return renew_splatnet_session(user)


@transaction.atomic
def renew_splatnet_session(user: models.User) -> models.SplatnetSession:
    nintendo_session = models.NintendoSession.objects.select_for_update().get(user=user)

    with httpx.Client() as client:
        web_service_token, bullet_token = splatnet.get_splatnet_session(
            client, nintendo_session.token
        )

    splatnet_session, created = models.SplatnetSession.objects.update_or_create(
        user=user,
        defaults={
            "web_service_token": web_service_token,
            "bullet_token": bullet_token,
        },
    )
    return splatnet_session


P = ParamSpec("P")
R = TypeVar("R")


def with_bullet_token(
    f: Callable[Concatenate[str, P], R]
) -> Callable[Concatenate[models.User, P], R]:
    def wrapper(user: models.User, *args: P.args, **kwargs: P.kwargs) -> R:
        splatnet_session = get_splatnet_session(user)
        try:
            return f(splatnet_session.bullet_token, *args, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                splatnet_session = renew_splatnet_session(user)
                return f(splatnet_session.bullet_token, *args, **kwargs)
            else:
                raise

    return wrapper


@with_bullet_token
def get_salmon_run_shifts(bullet_token: str) -> list[dict]:
    """
    Returns shifts in reverse chronological order (newest first).
    """
    with httpx.Client() as client:
        data = splatnet.get_salmon_run_jobs(client, bullet_token)
    shifts = []
    groups = data["data"]["coopResult"]["historyGroups"]["nodes"]
    for group in groups:
        for shift in group["historyDetails"]["nodes"]:
            shifts.append(shift)
    return shifts


def sync_salmon_run_shift_summaries(
    user: models.User,
) -> list[models.SalmonRunShiftSummaryRaw]:
    summaries = []
    num_new = 0
    # reverse shifts to get oldest first
    for shift in reversed(get_salmon_run_shifts(user)):
        summary, created = models.SalmonRunShiftSummaryRaw.objects.get_or_create(
            shift_id=shift["id"],
            uploaded_by=user,
            defaults={
                "data": shift,
            },
        )
        summaries.append(summary)
        if created:
            num_new += 1
    logger.info("synced shift summaries", user_id=user.id, num_new=num_new)
    return summaries


@with_bullet_token
def get_salmon_run_shift_detail(bullet_token: str, shift_id: str) -> dict:
    with httpx.Client() as client:
        return splatnet.get_salmon_run_job_detail(client, bullet_token, shift_id)


@transaction.atomic
def sync_salmon_run_shift_detail(
    user: models.User, raw: models.SalmonRunShiftSummaryRaw
) -> tuple[models.SalmonRunShiftDetailRaw, bool]:
    raw = models.SalmonRunShiftSummaryRaw.objects.select_for_update().get(pk=raw.pk)
    try:
        return (
            models.SalmonRunShiftDetailRaw.objects.get(
                uploaded_by=user, shift_id=raw.shift_id
            ),
            False,
        )
    except models.SalmonRunShiftDetailRaw.DoesNotExist:
        data = get_salmon_run_shift_detail(user, raw.shift_id)
        return (
            models.SalmonRunShiftDetailRaw.objects.create(
                shift_id=raw.shift_id,
                uploaded_by=user,
                data=data,
            ),
            True,
        )

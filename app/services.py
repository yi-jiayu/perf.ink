from typing import Callable, Concatenate, ParamSpec, TypeVar

import httpx
from django.db import transaction

import splatnet
from . import models

P = ParamSpec("P")
R = TypeVar("R")


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

    splatnet_session, created = models.SplatnetSession.objects.create_or_update(
        user=user,
        defaults={
            "web_service_token": web_service_token,
            "bullet_token": bullet_token,
        },
    )
    return splatnet_session


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


def sync_salmon_run_shifts(user: models.User) -> list[models.SalmonRunShiftSummaryRaw]:
    shifts = []
    # reverse shifts to get oldest first
    for shift in reversed(get_salmon_run_shifts(user)):
        shift, created = models.SalmonRunShiftSummaryRaw.objects.get_or_create(
            shift_id=shift["id"],
            uploaded_by=user,
            defaults={
                "data": shift,
            },
        )
        if created:
            shifts.append(shift)
    return shifts

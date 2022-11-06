import base64
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Concatenate, Iterable, ParamSpec, TypeVar

import httpx
import pendulum
import structlog
from django.db import transaction
from django.db.models import Avg, Max, QuerySet

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


@dataclass
class SummaryGroup:
    start_end_time: tuple[datetime, datetime]
    stage: str
    weapons: list[str]
    shifts: list[dict]


def group_salmon_run_jobs(data: dict) -> Iterable[SummaryGroup]:
    groups = data["data"]["coopResult"]["historyGroups"]["nodes"]
    for group in groups:
        start_end_time = (
            pendulum.parse(group["startTime"]),
            pendulum.parse(group["endTime"]),
        )
        shifts = group["historyDetails"]["nodes"]
        # there should always be at least one shift in a group
        stage = shifts[0]["coopStage"]["name"]
        weapons = [weapon["name"] for weapon in shifts[0]["weapons"]]

        yield SummaryGroup(
            start_end_time=start_end_time,
            stage=stage,
            weapons=weapons,
            shifts=shifts,
        )


@with_bullet_token
def get_summary_groups(bullet_token: str) -> list[SummaryGroup]:
    with httpx.Client() as client:
        data = splatnet.get_salmon_run_jobs(client, bullet_token)
    return list(group_salmon_run_jobs(data))


def get_played_at_from_shift_id(shift_id: str) -> datetime:
    decoded_shift_id = base64.standard_b64decode(shift_id).decode("utf-8")
    return pendulum.parse(decoded_shift_id[41:56])


@transaction.atomic
def sync_salmon_run_shift_summaries(
    user: models.User,
) -> list[models.SalmonRunShiftSummaryRaw]:
    groups = get_summary_groups(user)
    raw_summaries = []
    summaries = []
    # reverse groups to get oldest first
    for group in reversed(groups):
        rotation, created = models.SalmonRunRotation.objects.get_or_create(
            start_end_time=group.start_end_time,
            stage=group.stage,
            defaults={
                "weapons": group.weapons,
            },
        )
        # reverse shifts to get oldest first
        for shift in reversed(group.shifts):
            raw_summary = models.SalmonRunShiftSummaryRaw(
                rotation=rotation,
                shift_id=shift["id"],
                uploaded_by=user,
                data=shift,
                played_at=get_played_at_from_shift_id(shift["id"]),
            )
            raw_summaries.append(raw_summary)

            summary = models.SalmonRunShiftSummary.from_raw(user, rotation, shift)
            summaries.append(summary)

    models.SalmonRunShiftSummaryRaw.objects.bulk_create(
        raw_summaries, ignore_conflicts=True
    )
    summaries = models.SalmonRunShiftSummary.objects.bulk_create(
        summaries, ignore_conflicts=True
    )
    return summaries


@with_bullet_token
def get_salmon_run_shift_detail(bullet_token: str, shift_id: str) -> dict:
    with httpx.Client() as client:
        return splatnet.get_salmon_run_job_detail(client, bullet_token, shift_id)


@dataclass
class SalmonRunShiftStatistics:
    shifts_worked: int
    average_waves_cleared: float
    most_golden_eggs_delivered_team: int
    most_golden_eggs_delivered_self: int


def salmon_run_shift_statistics(shifts: QuerySet[models.SalmonRunShiftSummary]):
    shifts_worked = shifts.count()
    average_waves_cleared = shifts.aggregate(Avg("waves_cleared"))["waves_cleared__avg"]
    most_golden_eggs_delivered_team = shifts.aggregate(
        Max("golden_eggs_delivered_team")
    )["golden_eggs_delivered_team__max"]
    most_golden_eggs_delivered_self = shifts.aggregate(
        Max("golden_eggs_delivered_self")
    )["golden_eggs_delivered_self__max"]
    return SalmonRunShiftStatistics(
        shifts_worked=shifts_worked,
        average_waves_cleared=average_waves_cleared,
        most_golden_eggs_delivered_team=most_golden_eggs_delivered_team,
        most_golden_eggs_delivered_self=most_golden_eggs_delivered_self,
    )

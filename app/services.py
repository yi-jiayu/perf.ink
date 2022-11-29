import base64
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Concatenate, Iterable, ParamSpec, TypeVar

import httpx
import pendulum
import sentry_sdk
import structlog
from django.db import transaction
from django.db.models import Avg, Count, Max, QuerySet

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
) -> list[models.SalmonRunShiftSummary]:
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
    return models.SalmonRunShiftSummary.objects.bulk_create(
        summaries, ignore_conflicts=True
    )


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
    waves_cleared_by_water_level: dict[str, tuple[int, int, float]]
    waves_cleared_by_event: dict[str, tuple[int, int, float]]


def salmon_run_shift_statistics(
    shifts: QuerySet[models.SalmonRunShiftSummary],
    waves: QuerySet[models.SalmonRunWave],
):
    shifts_worked = shifts.count()
    average_waves_cleared = shifts.aggregate(Avg("waves_cleared"))["waves_cleared__avg"]
    most_golden_eggs_delivered_team = shifts.aggregate(
        Max("golden_eggs_delivered_team")
    )["golden_eggs_delivered_team__max"]
    most_golden_eggs_delivered_self = shifts.aggregate(
        Max("golden_eggs_delivered_self")
    )["golden_eggs_delivered_self__max"]
    waves_cleared_by_water_level_denominator = dict(
        waves.values("water_level")
        .annotate(Count("water_level"))
        .values_list("water_level", "water_level__count")
    )
    waves_cleared_by_water_level_numerator = dict(
        waves.filter(cleared=True)
        .values("water_level")
        .annotate(Count("water_level"))
        .values_list("water_level", "water_level__count")
    )
    waves_cleared_by_water_level = {}
    water_level_labels = {
        0: "Low",
        1: "Normal",
        2: "High",
    }
    for water_level, denominator in waves_cleared_by_water_level_denominator.items():
        numerator = waves_cleared_by_water_level_numerator.get(water_level, 0)
        waves_cleared_by_water_level[water_level_labels[water_level]] = (
            numerator,
            denominator,
            100 * numerator / denominator,
        )

    waves_faced_by_event_denominator = dict(
        waves.values("event")
        .annotate(Count("event"))
        .values_list("event", "event__count")
    )
    waves_cleared_by_event_numerator = dict(
        waves.filter(cleared=True)
        .values("event")
        .annotate(Count("event"))
        .values_list("event", "event__count")
    )
    waves_cleared_by_event = {}
    for event, denominator in waves_faced_by_event_denominator.items():
        numerator = waves_cleared_by_event_numerator.get(event, 0)
        event_label = event if event else "None"
        waves_cleared_by_event[event_label] = (
            numerator,
            denominator,
            100 * numerator / denominator,
        )

    return SalmonRunShiftStatistics(
        shifts_worked=shifts_worked,
        average_waves_cleared=average_waves_cleared,
        most_golden_eggs_delivered_team=most_golden_eggs_delivered_team,
        most_golden_eggs_delivered_self=most_golden_eggs_delivered_self,
        waves_cleared_by_water_level=waves_cleared_by_water_level,
        waves_cleared_by_event=waves_cleared_by_event,
    )


@transaction.atomic
def update_shift_with_details(
    shift: models.SalmonRunShiftSummary,
    details: dict,
):
    sentry_sdk.add_breadcrumb(data=details)

    if not details["data"]["coopHistoryDetail"]:
        # return if there is no coopHistoryDetail (e.g. when we try to fetch
        # details for a shift that is too old)
        return

    # load shift details
    models.SalmonRunShiftDetail.objects.create(
        summary=shift,
        hazard_level=details["data"]["coopHistoryDetail"]["dangerRate"] * 100,
        smell_meter=details["data"]["coopHistoryDetail"]["smellMeter"],
    )

    # load player results
    own_result = models.SalmonRunShiftPlayer.from_raw(
        shift,
        details["data"]["coopHistoryDetail"]["myResult"],
        is_uploader=True,
    )
    teammate_results = [
        models.SalmonRunShiftPlayer.from_raw(shift, result, is_uploader=False)
        for result in details["data"]["coopHistoryDetail"]["memberResults"]
    ]
    models.SalmonRunShiftPlayer.objects.bulk_create([own_result] + teammate_results)

    # load wave results
    wave_results = [
        models.SalmonRunWave.from_raw(shift, wave)
        for wave in details["data"]["coopHistoryDetail"]["waveResults"]
    ]
    models.SalmonRunWave.objects.bulk_create(wave_results)

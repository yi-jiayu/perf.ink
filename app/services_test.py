from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from . import factories, models, services


def test_get_played_at_from_shift_id():
    shift_id = "Q29vcEhpc3RvcnlEZXRhaWwtdS1xb21pZm92dG5wanZjaGRndm5tbToyMDIyMTAyNFQwODM2NDhfMGJiNmQ5MDctMTBlMC00NTM0LTkxMzktNTRhMzlhYmVjNjg3"
    got = services.get_played_at_from_shift_id(shift_id)
    want = datetime(2022, 10, 24, 8, 36, 48, tzinfo=timezone.utc)
    assert got == want


@pytest.fixture
def summary_groups(faker, raw_salmon_run_shift_factory):
    t0 = faker.date_time(tzinfo=timezone.utc)
    t1 = t0 + timedelta(days=1)
    t2 = t0 + timedelta(days=2)
    return [
        services.SummaryGroup(
            start_end_time=(t0, t1),
            stage="Gone Fission Hydroplant",
            weapons=["Aerospray MG", "Carbon Roller", "Explosher", "Jet Squelcher"],
            shifts=[raw_salmon_run_shift_factory() for _ in range(10)],
        ),
        services.SummaryGroup(
            start_end_time=(t1, t2),
            stage="Sockeye Station",
            weapons=[
                "Aerospray MG",
                "Undercover Brella",
                "Flingza Roller",
                "Heavy Splatling",
            ],
            shifts=[raw_salmon_run_shift_factory() for _ in range(10)],
        ),
    ]


@pytest.mark.django_db
def test_sync_salmon_run_shift_summaries(
    django_assert_max_num_queries,
    summary_groups,
):
    user = factories.UserFactory()
    with patch("app.services.get_summary_groups", return_value=summary_groups):
        with django_assert_max_num_queries(19):  # 20 summaries to sync - 1
            services.sync_salmon_run_shift_summaries(user)

        for group in summary_groups:
            rotation = models.SalmonRunRotation.objects.get(
                start_end_time=group.start_end_time,
                stage=group.stage,
                weapons=group.weapons,
            )
            for shift in group.shifts:
                assert models.SalmonRunShiftSummaryRaw.objects.filter(
                    rotation=rotation,
                    shift_id=shift["id"],
                    uploaded_by=user,
                    data=shift,
                    played_at=services.get_played_at_from_shift_id(shift["id"]),
                ).exists()

                assert models.SalmonRunShiftSummary.objects.filter(
                    rotation=rotation,
                    splatnet_id=shift["id"],
                    uploaded_by=user,
                    played_at=services.get_played_at_from_shift_id(shift["id"]),
                ).exists()

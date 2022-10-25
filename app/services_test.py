from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from . import factories, models, services


@pytest.fixture
def summary_groups(faker):
    t0 = timezone.now()
    t1 = t0 + timedelta(days=1)
    t2 = t0 + timedelta(days=2)
    return [
        services.SummaryGroup(
            start_end_time=(t0, t1),
            stage="Gone Fission Hydroplant",
            weapons=["Aerospray MG", "Carbon Roller", "Explosher", "Jet Squelcher"],
            shifts=[{"id": faker.uuid4(), "type": "summary"} for _ in range(10)],
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
            shifts=[{"id": faker.uuid4(), "type": "summary"} for _ in range(10)],
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
                ).exists()

import multiprocessing
from unittest.mock import call, patch

import pytest

from . import factories, models, tasks


@pytest.mark.django_db
def test_sync_salmon_run_shift_details():
    user = factories.UserFactory()
    raw_summaries = factories.SalmonRunShiftSummaryRawFactory.create_batch(
        10, uploaded_by=user
    )
    summaries = [
        factories.SalmonRunShiftSummaryFactory(
            uploaded_by=user, splatnet_id=raw_summary.shift_id
        )
        for raw_summary in raw_summaries
    ]

    # given that some shift details have already been synced
    for raw_summary in raw_summaries[:5]:
        factories.SalmonRunShiftDetailRawFactory(summary=raw_summary)
    for summary in summaries[:5]:
        factories.SalmonRunShiftDetailFactory(summary=summary)

    splatnet_shift_details = [
        {"id": raw_summary.shift_id, "type": "detail"}
        for raw_summary in raw_summaries[5:]
    ]

    with patch(
        "app.services.get_salmon_run_shift_detail",
        side_effect=splatnet_shift_details,
    ), patch("app.services.update_shift_with_details") as update_shift_with_details:
        tasks.sync_salmon_run_shift_details(
            user.id, [summary.shift_id for summary in raw_summaries]
        )

    update_shift_with_details.assert_has_calls(
        [
            call(summary, detail)
            for summary, detail in zip(summaries[5:], splatnet_shift_details[5:])
        ]
    )
    for raw_summary in raw_summaries[5:]:
        assert models.SalmonRunShiftDetailRaw.objects.filter(
            shift_id=raw_summary.shift_id,
            uploaded_by=user,
            data={"id": raw_summary.shift_id, "type": "detail"},
        ).exists()


@pytest.mark.django_db(transaction=True)
def _test_sync_salmon_run_shift_details_concurrency():
    """
    This test simulates the sync_salmon_run_shift_details task being run
    concurrently by multiple processes.

    The second process should block until the first completes and should not
    need to fetch any shift details because the first process would have synced
    them all.

    The latter condition is not automatically checked, but can be verified by
    inspecting the logs.

    This test is only for running manually, hence the underscore name prefix.
    """

    user = factories.UserFactory()
    summaries = factories.SalmonRunShiftSummaryRawFactory.create_batch(
        10, uploaded_by=user
    )

    code = """
import os

import django

os.environ.setdefault("DATABASE_URL", "postgres:///test_perf_ink")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "perf_ink.settings")
django.setup()

from unittest.mock import patch

from app import tasks

with patch(
    "app.services.get_salmon_run_shift_detail",
    return_value={"id": "foo", "detail": True},
):
    tasks.sync_salmon_run_shift_details(user_id, shift_ids)
"""

    context = {
        "user_id": user.id,
        "shift_ids": [summary.shift_id for summary in summaries],
    }
    p1 = multiprocessing.Process(
        target=exec,
        args=(
            code,
            context,
        ),
    )
    p2 = multiprocessing.Process(
        target=exec,
        args=(
            code,
            context,
        ),
    )

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    assert p1.exitcode == 0
    assert p2.exitcode == 0

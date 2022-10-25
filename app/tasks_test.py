import multiprocessing
import threading
import time
from unittest.mock import patch

import pytest

from . import factories, models, tasks


@pytest.mark.django_db
def test_sync_salmon_run_shift_details():
    user = factories.UserFactory()
    summaries = factories.SalmonRunShiftSummaryRawFactory.create_batch(
        10, uploaded_by=user
    )

    # given that some shift details have already been synced
    for summary in summaries[:5]:
        factories.SalmonRunShiftDetailRawFactory(summary=summary)

    def get_salmon_run_shift_detail(user, shift_id):
        return {"id": shift_id, "detail": True}

    with patch(
        "app.services.get_salmon_run_shift_detail",
        side_effect=get_salmon_run_shift_detail,
    ):
        tasks.sync_salmon_run_shift_details(
            user.id, [summary.shift_id for summary in summaries]
        )

    for summary in summaries:
        assert models.SalmonRunShiftDetailRaw.objects.filter(
            shift_id=summary.shift_id,
            uploaded_by=user,
            data={"id": summary.shift_id, "detail": True},
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

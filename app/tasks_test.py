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

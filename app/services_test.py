from unittest.mock import patch

import pytest

from . import factories, models, services


@pytest.mark.django_db
def test_sync_salmon_run_shift_summaries(faker, django_assert_max_num_queries):
    with patch("app.services.get_salmon_run_shifts") as get_salmon_run_shifts:
        user = factories.UserFactory()
        splatnet_shifts = [{"id": faker.uuid4()} for _ in range(10)]
        get_salmon_run_shifts.return_value = splatnet_shifts

        with django_assert_max_num_queries(10):
            services.sync_salmon_run_shift_summaries(user)

        for shift in splatnet_shifts:
            assert models.SalmonRunShiftSummaryRaw.objects.filter(
                shift_id=shift["id"],
                uploaded_by=user,
                data=shift,
            ).exists()


@pytest.mark.django_db
def test_sync_salmon_run_shift_summaries_only_new(faker, django_assert_max_num_queries):
    with patch("app.services.get_salmon_run_shifts") as get_salmon_run_shifts:
        user = factories.UserFactory()
        splatnet_shifts = [{"id": faker.uuid4()} for _ in range(10)]
        get_salmon_run_shifts.return_value = splatnet_shifts

        # given that some shift summaries have already been synced
        for shift in splatnet_shifts[:5]:
            models.SalmonRunShiftSummaryRaw.objects.create(
                shift_id=shift["id"],
                uploaded_by=user,
                data=shift,
            )

        with django_assert_max_num_queries(10):
            summaries = services.sync_salmon_run_shift_summaries(user)

        for shift in splatnet_shifts:
            assert models.SalmonRunShiftSummaryRaw.objects.filter(
                shift_id=shift["id"],
                uploaded_by=user,
                data=shift,
            ).exists()

        # then all the summaries should be returned, including those which were already synced
        assert len(summaries) == 10

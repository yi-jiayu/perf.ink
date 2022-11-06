import base64
from datetime import datetime, timezone

import factory

from . import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.User

    username = factory.Faker("user_name")
    email = factory.Faker("email")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class SalmonRunShiftSummaryRawFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SalmonRunShiftSummaryRaw

    played_at = factory.Faker("date_time", tzinfo=timezone.utc)
    data = factory.LazyAttribute(lambda self: {"id": self.shift_id})

    @factory.lazy_attribute
    def shift_id(self):
        uuid = factory.Faker("uuid4")
        played_at = self.played_at
        decoded_shift_id = (
            f"CoopHistoryDetail-u-qomifovtnpjvchdgvnmm:{played_at}_{uuid}"
        )
        return base64.standard_b64encode(decoded_shift_id.encode("utf-8")).decode(
            "utf-8"
        )


class SalmonRunShiftDetailRawFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SalmonRunShiftDetailRaw

    shift_id = factory.LazyAttribute(lambda self: self.summary.shift_id)
    data = factory.LazyAttribute(lambda self: {"id": self.shift_id, "detail": True})
    uploaded_by = factory.LazyAttribute(lambda self: self.summary.uploaded_by)


class SalmonRunRotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SalmonRunRotation

    start_end_time = (datetime(2022, 9, 30), datetime(2022, 10, 1, 16))
    stage = "Gone Fission Hydroplant"
    weapons = [
        "Splash-o-matic",
        "Octobrush",
        "Bloblobber",
        ".96 Gal",
    ]


class SalmonRunShiftSummaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SalmonRunShiftSummary

    splatnet_id = factory.Faker("uuid4")
    uploaded_by = factory.SubFactory(UserFactory)

    rotation = factory.SubFactory(SalmonRunRotationFactory)

    played_at = factory.Faker("date_time", tzinfo=timezone.utc)
    waves_cleared = 1
    grade = "Eggsecutive VP"
    grade_points = "200"
    grade_point_diff = "KEEP"
    golden_eggs_delivered_team = 20
    power_eggs_delivered_team = 200
    golden_eggs_delivered_self = 10
    power_eggs_delivered_self = 100
    king_salmonid = ""
    king_salmonid_defeated = False


class SalmonRunShiftDetailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SalmonRunShiftDetail

    summary = factory.SubFactory(SalmonRunShiftSummaryFactory)
    hazard_level = 120.0
    smell_meter = 3

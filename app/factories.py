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

    shift_id = factory.Faker("uuid4")
    data = factory.LazyAttribute(lambda self: {"id": self.shift_id})


class SalmonRunShiftDetailRawFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SalmonRunShiftDetailRaw

    shift_id = factory.LazyAttribute(lambda self: self.summary.shift_id)
    data = factory.LazyAttribute(lambda self: {"id": self.shift_id, "detail": True})
    uploaded_by = factory.LazyAttribute(lambda self: self.summary.uploaded_by)

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class NintendoSession(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField()


class SplatnetSession(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    web_service_token = models.TextField()
    bullet_token = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)


class SalmonRunShiftSummaryRaw(models.Model):
    shift_id = models.TextField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.JSONField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shift_id", "uploaded_by"],
                name="salmonrunshiftsummaryraw_unique",
            ),
        ]


class SalmonRunShiftDetailRaw(models.Model):
    shift_id = models.TextField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.JSONField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shift_id", "uploaded_by"],
                name="salmonrunshiftdetailraw_unique",
            )
        ]

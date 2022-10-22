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

    @property
    def hazard_level(self) -> float:
        return self.data["data"]["coopHistoryDetail"]["dangerRate"]

    @property
    def rank(self) -> str:
        return self.data["data"]["coopHistoryDetail"]["afterGrade"]["name"]

    @property
    def rank_points(self) -> int:
        return self.data["data"]["coopHistoryDetail"]["afterGradePoint"]

    @property
    def boss_count_individual(self) -> int:
        return self.data["data"]["coopHistoryDetail"]["myResult"]["defeatEnemyCount"]

    @property
    def boss_count_team(self):
        return self.boss_count_individual + sum(
            result["defeatEnemyCount"]
            for result in self.data["data"]["coopHistoryDetail"]["memberResults"]
        )

    @property
    def boss_count_percent(self):
        value = self.boss_count_individual / self.boss_count_team * 100
        return f"{value:.1f}%"

    @property
    def rescued_count_individual(self):
        return self.data["data"]["coopHistoryDetail"]["myResult"]["rescuedCount"]

    @property
    def rescued_count_team(self):
        return self.rescued_count_individual + sum(
            result["rescuedCount"]
            for result in self.data["data"]["coopHistoryDetail"]["memberResults"]
        )

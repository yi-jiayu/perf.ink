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

    @property
    def grade(self):
        return self.data["afterGrade"]["name"]

    @property
    def grade_points(self):
        return self.data["afterGradePoint"]

    @property
    def change(self):
        return self.data["gradePointDiff"]


class SalmonRunShiftDetailRaw(models.Model):
    summary = models.OneToOneField(
        SalmonRunShiftSummaryRaw, on_delete=models.CASCADE, related_name="detail"
    )
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
        return self.data["data"]["coopHistoryDetail"]["dangerRate"] * 100

    @property
    def hazard_level_formatted(self):
        return f"{self.hazard_level:.1f}%"

    @property
    def golden_eggs_delivered_individual(self):
        return self.data["data"]["coopHistoryDetail"]["myResult"]["goldenDeliverCount"]

    @property
    def golden_eggs_assisted_individual(self):
        return self.data["data"]["coopHistoryDetail"]["myResult"]["goldenAssistCount"]

    @property
    def golden_eggs_contributed_individual(self):
        return (
            self.golden_eggs_delivered_individual + self.golden_eggs_assisted_individual
        )

    @property
    def contributed_most_golden_eggs(self):
        """
        Returns true if the player delivered the most golden eggs.
        """
        return all(
            self.golden_eggs_contributed_individual
            > (teammate["goldenDeliverCount"] + teammate["goldenAssistCount"])
            for teammate in self.data["data"]["coopHistoryDetail"]["memberResults"]
        )

    @property
    def defeated_most_bosses(self):
        """
        Returns true if the player defeated the most bosses.
        """
        return all(
            self.data["data"]["coopHistoryDetail"]["myResult"]["defeatEnemyCount"]
            > teammate["defeatEnemyCount"]
            for teammate in self.data["data"]["coopHistoryDetail"]["memberResults"]
        )

    @property
    def grade(self) -> str:
        return self.data["data"]["coopHistoryDetail"]["afterGrade"]["name"]

    @property
    def grade_points(self) -> int:
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


# class SalmonRunRotation(models.Model):
#     start_end_time = DateTimeRangeField()
#     stage = models.TextField()
#     weapons = ArrayField(models.TextField())
#
#
# class SalmonRunShiftSummary(models.Model):
#     rotation = models.ForeignKey(SalmonRunRotation, on_delete=models.CASCADE, null=True)
#     uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     raw = models.ForeignKey(SalmonRunShiftSummaryRaw, on_delete=models.CASCADE)
#
#     grade = models.TextField()
#     grade_points = models.IntegerField()
#     change = models.TextField()
#
#
# class SalmonRunShiftDetail(models.Model):
#     summary = models.OneToOneField(SalmonRunShiftSummary, on_delete=models.CASCADE)
#     raw = models.ForeignKey(SalmonRunShiftDetailRaw, on_delete=models.CASCADE)
#
#     hazard_level = models.FloatField()
#
#
# class SalmonRunWave(models.Model):
#     shift = models.ForeignKey(SalmonRunShiftDetail, on_delete=models.CASCADE)
#
#     number = models.IntegerField()
#     cleared = models.BooleanField()
#     tide = models.TextField()
#     event = models.TextField()
#     quota = models.IntegerField()
#     delivered = models.IntegerField()
#     power_eggs = models.IntegerField()
#     specials_used = ArrayField(models.TextField())

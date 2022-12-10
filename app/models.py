import base64
from functools import cached_property
from typing import Optional

import pendulum
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField, DateTimeRangeField
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


class SalmonRunRotation(models.Model):
    start_end_time = DateTimeRangeField()
    stage = models.TextField()
    weapons = ArrayField(models.TextField())


class SalmonRunShiftSummaryRaw(models.Model):
    rotation = models.ForeignKey(
        SalmonRunRotation, null=True, on_delete=models.SET_NULL
    )
    shift_id = models.TextField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data = models.JSONField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    played_at = models.DateTimeField()

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

    @property
    def wave_results(self):
        return self.data["data"]["coopHistoryDetail"]["waveResults"]

    @property
    def king_salmonid(self):
        return self.data["data"]["coopHistoryDetail"]["bossResult"]["boss"]["name"]

    @property
    def player_results(self):
        return [self.data["data"]["coopHistoryDetail"]["myResult"]] + self.data["data"][
            "coopHistoryDetail"
        ]["memberResults"]

    @property
    def enemy_results(self):
        return self.data["data"]["coopHistoryDetail"]["enemyResults"]


result_wave_to_waves_cleared = {
    -1: -1,
    0: 3,
    1: 0,
    2: 1,
    3: 2,
}


class SalmonRunShiftSummary(models.Model):
    # candidate key
    splatnet_id = models.TextField()
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # supplementary information
    rotation = models.ForeignKey(
        SalmonRunRotation, on_delete=models.CASCADE, null=True, related_name="shifts"
    )

    # extracted fields
    played_at = models.DateTimeField()
    waves_cleared = models.IntegerField()
    grade = models.TextField()
    grade_points = models.IntegerField()
    grade_point_diff = models.TextField()
    golden_eggs_delivered_team = models.IntegerField()
    power_eggs_delivered_team = models.IntegerField()
    golden_eggs_delivered_self = models.IntegerField()
    power_eggs_delivered_self = models.IntegerField()
    king_salmonid = models.TextField()
    king_salmonid_defeated = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["splatnet_id", "uploaded_by"],
                name="salmonrunshiftsummary_unique",
            ),
        ]

    @staticmethod
    def _from_raw(user: User, rotation: SalmonRunRotation, raw: dict) -> dict:
        splatnet_id = raw["id"]
        decoded_splatnet_id = base64.standard_b64decode(splatnet_id).decode("utf-8")
        played_at = pendulum.parse(decoded_splatnet_id[41:56])

        golden_eggs_delivered_team = sum(wave["teamDeliverCount"] for wave in raw["waveResults"])
        power_eggs_delivered_team = raw["myResult"]["deliverCount"] + sum(
            teammate["deliverCount"] for teammate in raw["memberResults"]
        )
        king_salmonid = raw["bossResult"]["boss"]["name"] if raw["bossResult"] else ""
        king_salmonid_defeated = (
            raw["bossResult"]["hasDefeatBoss"] if raw["bossResult"] else False
        )
        return dict(
            rotation=rotation,
            uploaded_by=user,
            played_at=played_at,
            splatnet_id=splatnet_id,
            waves_cleared=result_wave_to_waves_cleared[raw["resultWave"]],
            grade=raw["afterGrade"]["name"],
            grade_points=raw["afterGradePoint"],
            grade_point_diff=raw["gradePointDiff"],
            golden_eggs_delivered_team=golden_eggs_delivered_team,
            power_eggs_delivered_team=power_eggs_delivered_team,
            golden_eggs_delivered_self=-1,  # no longer available in summary
            power_eggs_delivered_self=raw["myResult"]["deliverCount"],
            king_salmonid=king_salmonid,
            king_salmonid_defeated=king_salmonid_defeated,
        )

    @classmethod
    def from_raw(cls, user: User, rotation: SalmonRunRotation, raw: dict):
        return cls(**cls._from_raw(user, rotation, raw))

    @cached_property
    def squad(self):
        return list(self.players.all())

    @cached_property
    def own_result(self) -> Optional["SalmonRunShiftPlayer"]:
        for player in self.squad:
            if player.is_uploader:
                return player
        return None


class SalmonRunShiftDetail(models.Model):
    summary = models.OneToOneField(
        SalmonRunShiftSummary, on_delete=models.CASCADE, related_name="detail"
    )

    hazard_level = models.FloatField()
    smell_meter = models.IntegerField(null=True, blank=True)


class SalmonRunShiftPlayer(models.Model):
    shift = models.ForeignKey(
        SalmonRunShiftSummary, on_delete=models.CASCADE, related_name="players"
    )

    splatnet_id = models.TextField()
    is_uploader = models.BooleanField()
    bosses_defeated = models.IntegerField()
    golden_eggs_delivered = models.IntegerField()
    golden_eggs_assisted = models.IntegerField()
    power_eggs_delivered = models.IntegerField()
    teammates_rescued = models.IntegerField()
    times_rescued = models.IntegerField()
    special_weapon = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shift", "splatnet_id"],
                name="salmonrunshiftplayer_unique",
            ),
        ]

    @staticmethod
    def _from_raw(shift: SalmonRunShiftSummary, raw: dict, is_uploader: bool) -> dict:
        return {
            "shift": shift,
            "splatnet_id": raw["player"]["id"],
            "is_uploader": is_uploader,
            "bosses_defeated": raw["defeatEnemyCount"],
            "golden_eggs_delivered": raw["goldenDeliverCount"],
            "golden_eggs_assisted": raw["goldenAssistCount"],
            "power_eggs_delivered": raw["deliverCount"],
            "teammates_rescued": raw["rescueCount"],
            "times_rescued": raw["rescuedCount"],
            "special_weapon": raw["specialWeapon"]["name"]
            if raw["specialWeapon"]
            else "",
        }

    @classmethod
    def from_raw(cls, shift: SalmonRunShiftSummary, raw: dict, *, is_uploader: bool):
        return cls(**cls._from_raw(shift, raw, is_uploader))

    def defeated_most_bosses(self):
        return all(
            self.bosses_defeated >= member.bosses_defeated
            for member in self.shift.squad
        )

    @property
    def golden_eggs_contributed(self):
        return self.golden_eggs_delivered + self.golden_eggs_assisted

    def contributed_most_golden_eggs(self):
        return all(
            self.golden_eggs_contributed >= member.golden_eggs_contributed
            for member in self.shift.squad
        )


class SalmonRunWave(models.Model):
    shift = models.ForeignKey(
        SalmonRunShiftSummary, on_delete=models.CASCADE, related_name="waves"
    )

    number = models.IntegerField()
    cleared = models.BooleanField()
    water_level = models.IntegerField()
    event = models.TextField()
    golden_egg_quota = models.IntegerField()
    golden_eggs_delivered = models.IntegerField()
    specials_used = ArrayField(models.TextField())

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["shift", "number"],
                name="salmonrunwave_unique",
            ),
        ]

    @staticmethod
    def _from_raw(shift: SalmonRunShiftSummary, raw: dict) -> dict:
        if raw["waveNumber"] == 4:
            # king salmonid wave
            cleared = shift.king_salmonid_defeated
        else:
            # normal wave
            cleared = raw["waveNumber"] <= shift.waves_cleared
        return {
            "shift": shift,
            "number": raw["waveNumber"],
            "cleared": cleared,
            "water_level": raw["waterLevel"],
            "event": raw["eventWave"]["name"] if raw["eventWave"] else "",
            "golden_egg_quota": raw["deliverNorm"] if raw["deliverNorm"] else -1,
            "golden_eggs_delivered": raw["teamDeliverCount"]
            if raw["teamDeliverCount"]
            else -1,
            "specials_used": [special["name"] for special in raw["specialWeapons"]],
        }

    @classmethod
    def from_raw(cls, shift: SalmonRunShiftSummary, raw: dict):
        return cls(**cls._from_raw(shift, raw))

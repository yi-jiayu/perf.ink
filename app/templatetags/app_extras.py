from django import template

from .. import models

register = template.Library()


@register.simple_tag
def water_level_string(water_level: int):
    if water_level == 0:
        return "Low tide"
    elif water_level == 1:
        return "Normal"
    elif water_level == 2:
        return "High tide"
    else:
        raise ValueError(f"invalid water level: {water_level}")


@register.filter
def special_weapon_icon(name: str):
    icons = {
        "Killer Wail 5.1": "killer_wail_5_1.png",
        "Inkjet": "inkjet.png",
        "Triple Inkstrike": "triple_inkstrike.png",
        "Crab Tank": "crab_tank.png",
        "Booyah Bomb": "booyah_bomb.png",
        "Wave Breaker": "wave_breaker.png",
    }
    return icons[name]

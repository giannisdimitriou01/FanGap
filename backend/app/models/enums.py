from enum import Enum


class RatingSource(str, Enum):
    STEAM = "steam"
    OPENCRITIC = "opencritic"
    IGDB = "igdb"


class RatingAudience(str, Enum):
    CRITIC = "critic"
    FAN = "fan"

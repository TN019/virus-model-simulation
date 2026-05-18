from enum import Enum


class HealthState(str, Enum):
    SUSCEPTIBLE = "susceptible"
    INFECTIOUS = "infectious"
    IMMUNE = "immune"
    DEAD = "dead"

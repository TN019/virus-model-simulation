"""Health states used to classify agents in tick statistics."""

from enum import Enum


class HealthState(str, Enum):
    """Discrete health categories aligned with NetLogo reporters."""
    SUSCEPTIBLE = "susceptible"
    INFECTIOUS = "infectious"
    IMMUNE = "immune"
    DEAD = "dead"

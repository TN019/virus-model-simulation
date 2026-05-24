"""Agent state for one person (turtle) in the Virus ABM."""
from __future__ import annotations
from dataclasses import dataclass
from model.state import HealthState

@dataclass
class Person:
    """
    One individual in the world with position, age, and infection status.
    sick / remaining_immunity mirror NetLogo sick? and immune timers.
    """
    id: int
    x: float
    y: float
    heading: float
    age: int
    sick: bool = False
    sick_time: int = 0
    remaining_immunity: int = 0

    @property
    def immune(self) -> bool:
        """True while temporary immunity ticks remain."""
        return self.remaining_immunity > 0

    @property
    def health_state(self) -> HealthState:
        """Classify the person for aggregate statistics."""
        if self.sick:
            return HealthState.INFECTIOUS
        if self.immune:
            return HealthState.IMMUNE
        return HealthState.SUSCEPTIBLE

    def get_sick(self) -> None:
        """Become infectious and clear any immunity timer."""
        self.sick = True
        self.remaining_immunity = 0
        self.sick_time = 0

    def get_healthy(self) -> None:
        """Return to susceptible with no infection or immunity."""
        self.sick = False
        self.remaining_immunity = 0
        self.sick_time = 0

    def become_immune(self, immunity_duration: int) -> None:
        """Recover from infection and start an immunity countdown."""
        self.sick = False
        self.sick_time = 0
        self.remaining_immunity = immunity_duration

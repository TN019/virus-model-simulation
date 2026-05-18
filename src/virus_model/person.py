from __future__ import annotations

from dataclasses import dataclass

from virus_model.state import HealthState


@dataclass
class Person:
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
        return self.remaining_immunity > 0

    @property
    def health_state(self) -> HealthState:
        if self.sick:
            return HealthState.INFECTIOUS
        if self.immune:
            return HealthState.IMMUNE
        return HealthState.SUSCEPTIBLE

    def get_sick(self) -> None:
        self.sick = True
        self.remaining_immunity = 0
        self.sick_time = 0

    def get_healthy(self) -> None:
        self.sick = False
        self.remaining_immunity = 0
        self.sick_time = 0

    def become_immune(self, immunity_duration: int) -> None:
        self.sick = False
        self.sick_time = 0
        self.remaining_immunity = immunity_duration

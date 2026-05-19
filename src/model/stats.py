from __future__ import annotations

from dataclasses import dataclass

from model.person import Person
from model.state import HealthState


@dataclass(frozen=True)
class TickRecord:
    tick: int
    susceptible: int
    infected: int
    immune: int
    total: int
    percent_infected: float
    percent_immune: float


def population_counts(people: list[Person]) -> tuple[int, int, int, int]:
    infected = sum(1 for p in people if p.health_state == HealthState.INFECTIOUS)
    immune = sum(1 for p in people if p.health_state == HealthState.IMMUNE)
    total = len(people)
    susceptible = total - infected - immune
    return susceptible, infected, immune, total


def record_tick(tick: int, people: list[Person]) -> TickRecord:
    susceptible, infected, immune, total = population_counts(people)
    if total == 0:
        return TickRecord(tick, 0, 0, 0, 0, 0.0, 0.0)
    return TickRecord(
        tick=tick,
        susceptible=susceptible,
        infected=infected,
        immune=immune,
        total=total,
        percent_infected=(infected / total) * 100,
        percent_immune=(immune / total) * 100,
    )

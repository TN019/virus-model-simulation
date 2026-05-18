from __future__ import annotations

import random
from abc import ABC, abstractmethod

from virus_model.config import SimulationConfig
from virus_model.person import Person


class InfectionPolicy(ABC):
    @abstractmethod
    def try_infect(self, carrier: Person, others: list[Person], rng: random.Random) -> None:
        ...


class BaselineInfectionPolicy(InfectionPolicy):
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config

    def try_infect(self, carrier: Person, others: list[Person], rng: random.Random) -> None:
        if not carrier.sick:
            return
        for person in others:
            if person.id == carrier.id or person.sick or person.immune:
                continue
            if rng.random() * 100 < self.config.infectiousness:
                person.get_sick()


class ExtensionInfectionPolicy(BaselineInfectionPolicy):
    def try_infect(self, carrier: Person, others: list[Person], rng: random.Random) -> None:
        super().try_infect(carrier, others, rng)
        if not carrier.sick or self.config.immune_reinfection_probability <= 0:
            return
        for person in others:
            if person.id == carrier.id or person.sick or not person.immune:
                continue
            if rng.random() * 100 < self.config.immune_reinfection_probability:
                person.get_sick()

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections.abc import Callable

from model.config import SimulationConfig
from model.person import Person


class InfectionPolicy(ABC):
    @abstractmethod
    def try_infect(self, carrier: Person, others: list[Person], rng: random.Random) -> None:
        ...


class PrototypeInfectionPolicy(InfectionPolicy):
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


class ExtensionInfectionPolicy(PrototypeInfectionPolicy):
    def __init__(
        self,
        config: SimulationConfig,
        *,
        on_immune_reinfection: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(config)
        self._on_immune_reinfection = on_immune_reinfection

    def try_infect(self, carrier: Person, others: list[Person], rng: random.Random) -> None:
        super().try_infect(carrier, others, rng)
        if not carrier.sick or self.config.immune_reinfection_probability <= 0:
            return
        for person in others:
            if person.id == carrier.id or person.sick or not person.immune:
                continue
            if rng.random() * 100 < self.config.immune_reinfection_probability:
                person.get_sick()
                if self._on_immune_reinfection is not None:
                    self._on_immune_reinfection()

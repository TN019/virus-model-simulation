"""Infection policies: NetLogo prototype vs extension immune reinfection."""
from __future__ import annotations
import random
from abc import ABC, abstractmethod
from collections.abc import Callable
from model.config import SimulationConfig
from model.person import Person

class InfectionPolicy(ABC):
    """Strategy for transmission when a sick person shares a patch with others."""
    @abstractmethod
    def try_infect(self, carrier: Person, others: list[Person], rng: random.Random) -> None:
        """Attempt infection from carrier to co-located people (patch mates)."""
        ...


class PrototypeInfectionPolicy(InfectionPolicy):
    """NetLogo-aligned transmission: only non-sick, non-immune susceptibles."""
    def __init__(self, config: SimulationConfig) -> None:
        """Store simulation parameters for infectiousness rolls."""
        self.config = config

    def try_infect(self, carrier: Person, others: list[Person], rng: random.Random) -> None:
        """Roll infectiousness once per eligible patch mate."""
        if not carrier.sick:
            return
        for person in others:
            if person.id == carrier.id or person.sick or person.immune:
                continue
            if rng.random() * 100 < self.config.infectiousness:
                person.get_sick()


class ExtensionInfectionPolicy(PrototypeInfectionPolicy):
    """
    Adds immune reinfection: immune agents on the same patch may become sick again.
    Assumes on_immune_reinfection is called once per successful immune reinfection event.
    """
    def __init__(
        self,
        config: SimulationConfig,
        *,
        on_immune_reinfection: Callable[[], None] | None = None,
    ) -> None:
        """Extend prototype policy with optional reinfection callback."""
        super().__init__(config)
        self._on_immune_reinfection = on_immune_reinfection

    def try_infect(self, carrier: Person, others: list[Person], rng: random.Random) -> None:
        """Run prototype rules, then optionally reinfect immune patch mates."""
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

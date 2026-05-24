"""Main tick loop for the Virus agent-based model."""
from __future__ import annotations
import random
from collections.abc import Callable
from model.config import SimulationConfig
from model.person import Person
from model.policies import (
    ExtensionInfectionPolicy,
    InfectionPolicy,
    PrototypeInfectionPolicy,
)
from model.stats import TickRecord, record_tick
from model.world import World

def _default_policy(
    config: SimulationConfig,
    *,
    on_immune_reinfection: Callable[[], None] | None = None,
) -> InfectionPolicy:
    """Pick extension policy when immune_reinfection_probability > 0, else prototype."""
    if config.immune_reinfection_probability > 0:
        return ExtensionInfectionPolicy(config, on_immune_reinfection=on_immune_reinfection)
    return PrototypeInfectionPolicy(config)

class VirusSimulation:
    """
    One stochastic replicate of the Virus model.
    Tracks immune_reinfections and cumulative_reinfections_by_tick for extension export.
    """
    def __init__(
        self,
        config: SimulationConfig,
        *,
        seed: int | None = None,
        policy: InfectionPolicy | None = None,
    ) -> None:
        """Wire config, RNG, world, and infection policy for one replicate."""
        self.config = config
        self.seed = seed if seed is not None else config.base_seed
        self.rng = random.Random(self.seed)
        self.world = World(config, self.rng)
        self.immune_reinfections = 0
        self.cumulative_reinfections_by_tick: list[int] = []
        self.policy = policy or _default_policy(
            config,
            on_immune_reinfection=self._record_immune_reinfection,
        )

    def _record_immune_reinfection(self) -> None:
        """Increment the per-run immune reinfection counter (extension metric)."""
        self.immune_reinfections += 1

    def setup(self) -> None:
        """Reset counters and initialize the world population."""
        self.immune_reinfections = 0
        self.cumulative_reinfections_by_tick = [0]
        self.world.setup()

    def step(self) -> None:
        """
        Advance the model by one tick in NetLogo order.
        Age and remove dead, move, recover or die from infection, infect/reproduce,
        then record cumulative reinfections at end of tick (via run()).
        """
        people = self.world.people
        self.rng.shuffle(people)
        self.world.people = [person for person in people if self._get_older(person)]

        self.rng.shuffle(self.world.people)
        for person in self.world.people:
            self.world.move(person)

        self.rng.shuffle(self.world.people)
        self.world.people = [
            person for person in self.world.people if self._recover_or_stay_alive(person)
        ]

        grouped = self.world.people_by_patch()
        order = list(self.world.people)
        self.rng.shuffle(order)
        for person in order:
            if person.sick:
                patch = self.world.patch_key(person)
                self.policy.try_infect(person, grouped[patch], self.rng)
            else:
                self._reproduce(person)

    def run(self, ticks: int | None = None) -> list[TickRecord]:
        """Run setup and ticks; return tick 0..N records inclusive."""
        total_ticks = ticks if ticks is not None else self.config.ticks
        self.setup()
        records = [record_tick(0, self.world.people)]
        for tick in range(1, total_ticks + 1):
            self.step()
            records.append(record_tick(tick, self.world.people))
            self.cumulative_reinfections_by_tick.append(self.immune_reinfections)
        return records

    def _get_older(self, person: Person) -> bool:
        """Age one tick; return False if the person dies of old age."""
        person.age += 1
        if person.age > self.config.lifespan:
            return False
        if person.immune:
            person.remaining_immunity -= 1
        if person.sick:
            person.sick_time += 1
        return True

    def _recover_or_stay_alive(self, person: Person) -> bool:
        """
        After duration sick ticks, roll chance_recover to become immune.
        Assumes callers only invoke when sick_time may exceed duration.
        """
        if not person.sick or person.sick_time <= self.config.duration:
            return True
        if self.rng.random() * 100 < self.config.chance_recover:
            person.become_immune(self.config.immunity_duration)
            return True
        return False

    def _reproduce(self, person: Person) -> None:
        """Hatch one offspring if under carrying capacity and reproduction roll succeeds."""
        if len(self.world.people) >= self.config.carrying_capacity:
            return
        if self.rng.random() * 100 < self.config.chance_reproduce:
            self.world.people.append(self.world.hatch_offspring(person))

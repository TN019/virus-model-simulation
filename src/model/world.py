from __future__ import annotations

import math
import random
from collections import defaultdict

from model.config import SimulationConfig
from model.person import Person


class World:
    def __init__(self, config: SimulationConfig, rng: random.Random) -> None:
        self.config = config
        self.rng = rng
        self.size = config.world_size
        self.half = self.size // 2
        self.people: list[Person] = []
        self._next_id = 0

    def setup(self) -> None:
        self.people.clear()
        self._next_id = 0
        for _ in range(self.config.number_people):
            self.people.append(self._create_person(sick=False))
        for person in self.rng.sample(self.people, self.config.initial_infected):
            person.get_sick()

    def _create_person(
        self,
        *,
        sick: bool,
        x: float | None = None,
        y: float | None = None,
        heading: float | None = None,
        age: int | None = None,
    ) -> Person:
        person = Person(
            id=self._next_id,
            x=x if x is not None else self.rng.uniform(-self.half, self.half),
            y=y if y is not None else self.rng.uniform(-self.half, self.half),
            heading=heading if heading is not None else self.rng.uniform(0, 360),
            age=age if age is not None else self.rng.randrange(self.config.lifespan),
        )
        self._next_id += 1
        if sick:
            person.get_sick()
        else:
            person.get_healthy()
        return person

    def wrap(self, x: float, y: float) -> tuple[float, float]:
        return self._wrap_axis(x), self._wrap_axis(y)

    def _wrap_axis(self, value: float) -> float:
        limit = self.half
        while value > limit:
            value -= self.size
        while value < -limit:
            value += self.size
        return value

    def patch_key(self, person: Person) -> tuple[int, int]:
        return (int(round(person.x)), int(round(person.y)))

    def people_by_patch(self) -> dict[tuple[int, int], list[Person]]:
        grouped: dict[tuple[int, int], list[Person]] = defaultdict(list)
        for person in self.people:
            grouped[self.patch_key(person)].append(person)
        return grouped

    def move(self, person: Person) -> None:
        person.heading = (person.heading + self.rng.randint(0, 99) - self.rng.randint(0, 99)) % 360
        radians = math.radians(person.heading)
        person.x, person.y = self.wrap(
            person.x + math.sin(radians),
            person.y + math.cos(radians),
        )

    def hatch_offspring(self, parent: Person) -> Person:
        heading = (parent.heading - 45) % 360
        radians = math.radians(heading)
        x, y = self.wrap(parent.x + math.sin(radians), parent.y + math.cos(radians))
        return self._create_person(sick=False, x=x, y=y, heading=heading, age=1)

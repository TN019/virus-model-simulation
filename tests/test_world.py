import random

from virus_model.config import SimulationConfig
from virus_model.world import World


def test_wraps_coordinates_on_torus() -> None:
    world = World(SimulationConfig(world_size=33), random.Random(0))
    x, y = world.wrap(20.0, -20.0)
    assert x == -13.0
    assert y == 13.0


def test_setup_creates_expected_population() -> None:
    config = SimulationConfig(number_people=20, initial_infected=3)
    world = World(config, random.Random(1))
    world.setup()
    assert len(world.people) == 20
    assert sum(1 for person in world.people if person.sick) == 3

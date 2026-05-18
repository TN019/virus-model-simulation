import random

from virus_model.config import SimulationConfig
from virus_model.person import Person
from virus_model.policies import BaselineInfectionPolicy


def test_infection_only_affects_susceptibles_on_same_patch() -> None:
    config = SimulationConfig(infectiousness=100)
    policy = BaselineInfectionPolicy(config)
    rng = random.Random(0)

    carrier = Person(id=0, x=0.0, y=0.0, heading=0.0, age=1)
    carrier.get_sick()
    susceptible = Person(id=1, x=0.0, y=0.0, heading=0.0, age=1)
    immune = Person(id=2, x=0.0, y=0.0, heading=0.0, age=1)
    immune.become_immune(5)

    policy.try_infect(carrier, [carrier, susceptible, immune], rng)

    assert susceptible.sick
    assert not immune.sick

from virus_model.config import SimulationConfig
from virus_model.person import Person
from virus_model.simulation import VirusSimulation


def test_recovery_when_chance_recover_is_full() -> None:
    config = SimulationConfig(duration=1, chance_recover=100, immunity_duration=10)
    simulation = VirusSimulation(config, seed=0)
    person = Person(id=0, x=0.0, y=0.0, heading=0.0, age=1)
    person.get_sick()
    person.sick_time = 2
    simulation.world.people = [person]

    assert simulation._recover_or_stay_alive(person)
    assert person.immune
    assert not person.sick


def test_death_when_chance_recover_is_zero() -> None:
    config = SimulationConfig(duration=1, chance_recover=0)
    simulation = VirusSimulation(config, seed=0)
    person = Person(id=0, x=0.0, y=0.0, heading=0.0, age=1)
    person.get_sick()
    person.sick_time = 2
    simulation.world.people = [person]

    assert not simulation._recover_or_stay_alive(person)

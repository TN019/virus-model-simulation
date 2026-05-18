from virus_model.config import SimulationConfig
from virus_model.person import Person
from virus_model.simulation import VirusSimulation


def test_immune_individual_can_reproduce() -> None:
    config = SimulationConfig(chance_reproduce=100, carrying_capacity=300)
    simulation = VirusSimulation(config, seed=0)
    parent = Person(id=0, x=0.0, y=0.0, heading=0.0, age=10)
    parent.become_immune(5)
    simulation.world.people = [parent]

    simulation._reproduce(parent)

    assert len(simulation.world.people) == 2
    assert simulation.world.people[1].age == 1
    assert not simulation.world.people[1].sick
    assert not simulation.world.people[1].immune


def test_infectious_individual_does_not_reproduce_in_step() -> None:
    config = SimulationConfig(chance_reproduce=100)
    simulation = VirusSimulation(config, seed=0)
    person = Person(id=0, x=0.0, y=0.0, heading=0.0, age=10)
    person.get_sick()
    simulation.world.people = [person]

    simulation.step()

    assert len(simulation.world.people) == 1

from virus_model.config import SimulationConfig
from virus_model.simulation import VirusSimulation
from virus_model.stats import population_counts


def test_run_produces_tick_records() -> None:
    config = SimulationConfig(number_people=30, initial_infected=2, ticks=5, runs=1)
    records = VirusSimulation(config, seed=1).run()
    assert len(records) == 6
    assert records[0].total == 30


def test_immunity_expires_after_duration() -> None:
    config = SimulationConfig(
        number_people=1,
        initial_infected=0,
        immunity_duration=2,
        ticks=3,
        chance_reproduce=0,
    )
    simulation = VirusSimulation(config, seed=0)
    simulation.setup()
    simulation.world.people[0].become_immune(2)

    simulation.step()
    assert simulation.world.people[0].immune
    simulation.step()
    assert not simulation.world.people[0].immune

    susceptible, infected, immune, total = population_counts(simulation.world.people)
    assert susceptible == 1
    assert infected == 0
    assert immune == 0

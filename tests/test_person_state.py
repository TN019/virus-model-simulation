from virus_model.person import Person
from virus_model.state import HealthState


def test_health_states() -> None:
    person = Person(id=0, x=0.0, y=0.0, heading=0.0, age=1)
    assert person.health_state == HealthState.SUSCEPTIBLE

    person.get_sick()
    assert person.health_state == HealthState.INFECTIOUS

    person.become_immune(10)
    assert person.health_state == HealthState.IMMUNE

    person.get_healthy()
    assert person.health_state == HealthState.SUSCEPTIBLE

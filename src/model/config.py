from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SimulationConfig:
    name: str = "prototype"
    number_people: int = 150
    initial_infected: int = 10
    infectiousness: float = 50.0
    duration: int = 20
    chance_recover: float = 75.0
    ticks: int = 52
    runs: int = 100
    world_size: int = 35
    lifespan: int = 2600
    carrying_capacity: int = 300
    immunity_duration: int = 52
    chance_reproduce: float = 1.0
    immune_reinfection_probability: float = 0.0
    base_seed: int = 0

    @classmethod
    def from_json(cls, path: str | Path) -> SimulationConfig:
        data = json.loads(Path(path).read_text())
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

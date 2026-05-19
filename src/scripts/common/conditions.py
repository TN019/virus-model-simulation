from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from model.config import SimulationConfig

_SRC_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOTYPE_DIR = _SRC_ROOT / "configs" / "prototype"
DEFAULT_EXTENSION_DIR = _SRC_ROOT / "configs" / "extension"


@dataclass(frozen=True)
class ConditionSpec:
    name: str
    output_file: str
    infectiousness: float
    chance_recover: float
    immune_reinfection_probability: float = 0.0
    number_people: int = 150
    initial_infected: int = 10
    duration: int = 20
    ticks: int = 52
    runs: int = 100
    world_size: int = 35
    lifespan: int = 2600
    carrying_capacity: int = 300
    immunity_duration: int = 52
    chance_reproduce: float = 1.0
    base_seed: int = 0

    @classmethod
    def from_json(cls, path: str | Path) -> ConditionSpec:
        data = json.loads(Path(path).read_text())
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_config(
        self,
        *,
        runs: int | None = None,
        ticks: int | None = None,
        base_seed: int | None = None,
    ) -> SimulationConfig:
        return SimulationConfig(
            name=self.name,
            number_people=self.number_people,
            initial_infected=self.initial_infected,
            infectiousness=self.infectiousness,
            duration=self.duration,
            chance_recover=self.chance_recover,
            ticks=ticks if ticks is not None else self.ticks,
            runs=runs if runs is not None else self.runs,
            world_size=self.world_size,
            lifespan=self.lifespan,
            carrying_capacity=self.carrying_capacity,
            immunity_duration=self.immunity_duration,
            chance_reproduce=self.chance_reproduce,
            immune_reinfection_probability=self.immune_reinfection_probability,
            base_seed=base_seed if base_seed is not None else self.base_seed,
        )


def load_conditions(config_dir: str | Path) -> tuple[ConditionSpec, ...]:
    directory = Path(config_dir)
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise FileNotFoundError(f"No condition configs found in {directory}")
    return tuple(ConditionSpec.from_json(path) for path in paths)

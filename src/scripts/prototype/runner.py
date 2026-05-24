"""Execute replication (prototype) experiments and export CSVs."""
from __future__ import annotations
from pathlib import Path
from model.simulation import VirusSimulation
from model.stats import TickRecord
from scripts.common.conditions import ConditionSpec
from scripts.common.console import print_condition_done, print_condition_start
from scripts.common.export import write_behaviorspace_spreadsheet


def run_condition(
    spec: ConditionSpec,
    *,
    output_dir: Path,
    runs: int | None = None,
    ticks: int | None = None,
    base_seed: int | None = None,
    show_progress: bool = True,
) -> Path:
    """
    Run all replicates for one condition and write one BehaviorSpace CSV.
    Assumes run i uses seed base_seed + i (from config or CLI override).
    """
    config = spec.to_config(runs=runs, ticks=ticks, base_seed=base_seed)
    total_runs = config.runs
    all_runs: list[list[TickRecord]] = []

    for run_id in range(total_runs):
        if show_progress:
            print_condition_start(spec.name, run_id, total_runs)
        seed = config.base_seed + run_id
        records = VirusSimulation(config, seed=seed).run()
        all_runs.append(records)

    output_path = output_dir / spec.output_file
    write_behaviorspace_spreadsheet(
        output_path,
        experiment_name=f"{spec.name}_{total_runs}_runs",
        config=config,
        all_runs=all_runs,
    )
    if show_progress:
        print_condition_done(spec.name, str(output_path))
    return output_path


def run_all(
    conditions: tuple[ConditionSpec, ...],
    *,
    output_dir: Path,
    runs: int | None = None,
    ticks: int | None = None,
    base_seed: int | None = None,
) -> list[Path]:
    """Run every condition in order; return paths to written spreadsheet CSVs."""
    paths: list[Path] = []
    for spec in conditions:
        paths.append(
            run_condition(
                spec,
                output_dir=output_dir,
                runs=runs,
                ticks=ticks,
                base_seed=base_seed,
            )
        )
    return paths

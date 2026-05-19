from __future__ import annotations

import json
from pathlib import Path

from model.simulation import VirusSimulation
from model.stats import TickRecord

from scripts.common.conditions import ConditionSpec
from scripts.common.console import print_condition_done, print_condition_start
from scripts.common.export import write_behaviorspace_spreadsheet


def run_extension_condition(
    spec: ConditionSpec,
    *,
    output_dir: Path,
    runs: int | None = None,
    ticks: int | None = None,
    base_seed: int | None = None,
    show_progress: bool = True,
) -> tuple[Path, Path]:
    config = spec.to_config(runs=runs, ticks=ticks, base_seed=base_seed)
    total_runs = config.runs
    all_runs: list[list[TickRecord]] = []
    reinfection_counts: list[int] = []
    cumulative_by_run: list[list[int]] = []

    for run_id in range(total_runs):
        if show_progress:
            print_condition_start(spec.name, run_id, total_runs)
        seed = config.base_seed + run_id
        simulation = VirusSimulation(config, seed=seed)
        records = simulation.run()
        all_runs.append(records)
        reinfection_counts.append(simulation.immune_reinfections)
        cumulative_by_run.append(simulation.cumulative_reinfections_by_tick)

    output_path = output_dir / spec.output_file
    write_behaviorspace_spreadsheet(
        output_path,
        experiment_name=f"{spec.name}_{total_runs}_runs",
        config=config,
        all_runs=all_runs,
    )

    metrics_path = output_dir / f"{spec.name}_run_metrics.json"
    metrics_path.write_text(
        json.dumps(
            {
                "condition": spec.name,
                "immune_reinfection_probability": spec.immune_reinfection_probability,
                "ticks": config.ticks,
                "runs": total_runs,
                "immune_reinfections_per_run": reinfection_counts,
                "cumulative_reinfections_by_run": cumulative_by_run,
            },
            indent=2,
        )
    )

    if show_progress:
        print_condition_done(spec.name, str(output_path))
    return output_path, metrics_path


def run_all_extension(
    conditions: tuple[ConditionSpec, ...],
    *,
    output_dir: Path,
    runs: int | None = None,
    ticks: int | None = None,
    base_seed: int | None = None,
) -> list[Path]:
    paths: list[Path] = []
    for spec in conditions:
        csv_path, metrics_path = run_extension_condition(
            spec,
            output_dir=output_dir,
            runs=runs,
            ticks=ticks,
            base_seed=base_seed,
        )
        paths.append(csv_path)
        paths.append(metrics_path)
    return paths

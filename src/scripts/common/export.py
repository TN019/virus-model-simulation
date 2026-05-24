"""Write BehaviorSpace Spreadsheet v2 CSV files for NetLogo comparison."""
from __future__ import annotations
import csv
import statistics
from datetime import datetime, timezone
from pathlib import Path
from model.config import SimulationConfig
from model.stats import TickRecord

# Number of metric columns per run in BehaviorSpace spreadsheet layout.
METRICS_PER_RUN = 8

# Column headers for each run block (NetLogo reporter names).
METRIC_HEADERS = (
    "[step]",
    "ticks",
    "count turtles with [sick?]",
    "count turtles with [immune?]",
    "count turtles with [not sick? and not immune?]",
    "count turtles",
    "%infected",
    "%immune",
)


def _repeat_run_numbers(num_runs: int) -> list[str]:
    """Flatten run indices 1..N repeated for each metric column."""
    return [str(run_id) for run_id in range(1, num_runs + 1) for _ in range(METRICS_PER_RUN)]


def _repeat_metric_headers(num_runs: int) -> list[str]:
    """Repeat METRIC_HEADERS once per run for wide spreadsheet columns."""
    return list(METRIC_HEADERS) * num_runs


def _final_metric_columns(records: list[TickRecord]) -> list[str]:
    """Format the last tick of one run as eight BehaviorSpace metric strings."""
    final = records[-1]
    return [
        str(final.tick),
        str(final.tick),
        str(final.infected),
        str(final.immune),
        str(final.susceptible),
        str(final.total),
        str(final.percent_infected),
        str(final.percent_immune),
    ]


def _temporal_stat_row(
    label: str,
    all_runs: list[list[TickRecord]],
    reducer,
) -> list[str]:
    """Per-run min/max/mean over ticks (matches BehaviorSpace summary rows)."""
    row = [label]
    for run in all_runs:
        row.extend(
            [
                str(int(reducer([record.tick for record in run]))),
                str(int(reducer([record.tick for record in run]))),
                str(reducer([record.infected for record in run])),
                str(reducer([record.immune for record in run])),
                str(reducer([record.susceptible for record in run])),
                str(reducer([record.total for record in run])),
                str(reducer([record.percent_infected for record in run])),
                str(reducer([record.percent_immune for record in run])),
            ]
        )
    return row


def write_behaviorspace_spreadsheet(
    path: Path,
    *,
    experiment_name: str,
    config: SimulationConfig,
    all_runs: list[list[TickRecord]],
) -> None:
    """
    Write one BehaviorSpace Spreadsheet v2 file for all runs of a condition.
    Layout: metadata rows, per-run parameter rows, summary rows, then all tick data.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    num_runs = len(all_runs)
    half = config.world_size // 2

    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["BehaviorSpace results (Python virus-model)", "Spreadsheet version 2.0"])
        writer.writerow(["Virus (Python replication)"])
        writer.writerow([experiment_name])
        timestamp = datetime.now(timezone.utc).astimezone().isoformat(
            timespec="milliseconds",
        )
        writer.writerow([timestamp])
        writer.writerow(["min-pxcor", "max-pxcor", "min-pycor", "max-pycor"])
        writer.writerow([str(-half), str(half), str(-half), str(half)])

        writer.writerow(["[run number]", *_repeat_run_numbers(num_runs)])
        writer.writerow(
            ["duration", *[str(config.duration) for _ in range(num_runs * METRICS_PER_RUN)]]
        )
        writer.writerow(
            [
                "number-people",
                *[str(config.number_people) for _ in range(num_runs * METRICS_PER_RUN)],
            ]
        )
        writer.writerow(
            [
                "chance-recover",
                *[str(int(config.chance_recover)) for _ in range(num_runs * METRICS_PER_RUN)],
            ]
        )
        writer.writerow(["turtle-shape", *["person" for _ in range(num_runs * METRICS_PER_RUN)]])
        writer.writerow(
            [
                "infectiousness",
                *[str(int(config.infectiousness)) for _ in range(num_runs * METRICS_PER_RUN)],
            ]
        )
        if config.immune_reinfection_probability > 0:
            probability = config.immune_reinfection_probability
            writer.writerow(
                [
                    "immune-reinfection-probability",
                    *[str(probability) for _ in range(num_runs * METRICS_PER_RUN)],
                ]
            )

        writer.writerow(["[reporter]", *_repeat_metric_headers(num_runs)])

        writer.writerow(
            ["[final]", *[value for run in all_runs for value in _final_metric_columns(run)]]
        )
        writer.writerow(_temporal_stat_row("[min]", all_runs, min))
        writer.writerow(_temporal_stat_row("[max]", all_runs, max))
        writer.writerow(_temporal_stat_row("[mean]", all_runs, statistics.mean))
        writer.writerow(
            ["[total steps]", *[str(config.ticks) for _ in range(num_runs * METRICS_PER_RUN)]]
        )
        writer.writerow([])

        # All runs interleaved: one row per tick, columns grouped by run.
        writer.writerow(["[all run data]", *_repeat_metric_headers(num_runs)])
        num_ticks = len(all_runs[0])
        for tick_idx in range(num_ticks):
            row: list[str] = [""]
            for run in all_runs:
                record = run[tick_idx]
                row.extend(
                    [
                        str(record.tick),
                        str(record.tick),
                        str(record.infected),
                        str(record.immune),
                        str(record.susceptible),
                        str(record.total),
                        str(record.percent_infected),
                        str(record.percent_immune),
                    ]
                )
            writer.writerow(row)

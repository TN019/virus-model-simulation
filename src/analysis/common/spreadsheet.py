from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from pathlib import Path

METRICS_PER_RUN = 8
METRIC_INDEX = {
    "step": 0,
    "ticks": 1,
    "infected": 2,
    "immune": 3,
    "susceptible": 4,
    "total": 5,
    "percent_infected": 6,
    "percent_immune": 7,
}


@dataclass(frozen=True)
class SeriesStats:
    mean: list[float]
    std: list[float]


@dataclass(frozen=True)
class TickStats:
    tick: list[int]
    sick: SeriesStats
    immune: SeriesStats
    healthy: SeriesStats
    total: SeriesStats


@dataclass(frozen=True)
class TickSeries:
    tick: list[int]
    infected: list[float]
    immune: list[float]
    susceptible: list[float]
    total: list[float]
    percent_infected: list[float]
    percent_immune: list[float]


@dataclass(frozen=True)
class RunSummary:
    peak_sick: float
    peak_week: int
    final_sick: float
    final_immune: float
    final_healthy: float
    final_total: float


def _parse_float(value: str) -> float:
    value = value.strip()
    if not value:
        return 0.0
    return float(value)


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def _load_run_rows(path: Path) -> tuple[int, list[dict[str, list[float]]]]:
    rows = list(csv.reader(path.open(newline="")))
    reporter_row = next(i for i, row in enumerate(rows) if row and row[0] == "[reporter]")
    num_runs = (len(rows[reporter_row]) - 1) // METRICS_PER_RUN
    data_start = next(i for i, row in enumerate(rows) if row and row[0] == "[all run data]") + 1

    tick_rows: list[dict[str, list[float]]] = []
    for row in rows[data_start:]:
        if len(row) < 3 or not row[1].strip().isdigit():
            continue
        metrics: dict[str, list[float]] = {key: [] for key in METRIC_INDEX}
        for run_idx in range(num_runs):
            base = 1 + run_idx * METRICS_PER_RUN
            for name, offset in METRIC_INDEX.items():
                metrics[name].append(_parse_float(row[base + offset]))
        tick_rows.append(metrics)
    return num_runs, tick_rows


def load_tick_stats(path: str | Path) -> TickStats:
    """Per-tick mean and sample SD across all runs."""
    _, tick_rows = _load_run_rows(Path(path))

    def band(key: str) -> SeriesStats:
        means = [statistics.mean(row[key]) for row in tick_rows]
        stds = [_std(row[key]) for row in tick_rows]
        return SeriesStats(mean=means, std=stds)

    return TickStats(
        tick=[int(statistics.mean(row["ticks"])) for row in tick_rows],
        sick=band("infected"),
        immune=band("immune"),
        healthy=band("susceptible"),
        total=band("total"),
    )


def load_tick_series(path: str | Path) -> TickSeries:
    """Per-tick means only (backward compatible)."""
    _, tick_rows = _load_run_rows(Path(path))
    infected = [statistics.mean(row["infected"]) for row in tick_rows]
    immune = [statistics.mean(row["immune"]) for row in tick_rows]
    total = [statistics.mean(row["total"]) for row in tick_rows]
    percent_infected = [statistics.mean(row["percent_infected"]) for row in tick_rows]
    percent_immune = [statistics.mean(row["percent_immune"]) for row in tick_rows]
    return TickSeries(
        tick=[int(statistics.mean(row["ticks"])) for row in tick_rows],
        infected=infected,
        immune=immune,
        susceptible=[statistics.mean(row["susceptible"]) for row in tick_rows],
        total=total,
        percent_infected=percent_infected,
        percent_immune=percent_immune,
    )


def load_per_run_series(path: str | Path) -> list[dict[str, list[float]]]:
    """Per-run time series extracted from a BehaviorSpace spreadsheet."""
    num_runs, tick_rows = _load_run_rows(Path(path))
    runs: list[dict[str, list[float]]] = [
        {key: [] for key in METRIC_INDEX} for _ in range(num_runs)
    ]
    for row in tick_rows:
        for run_idx in range(num_runs):
            for key in METRIC_INDEX:
                runs[run_idx][key].append(row[key][run_idx])
    return runs


def load_per_run_summaries(path: str | Path) -> list[RunSummary]:
    """One summary row per stochastic run."""
    num_runs, tick_rows = _load_run_rows(Path(path))
    summaries: list[RunSummary] = []

    for run_idx in range(num_runs):
        sick = [row["infected"][run_idx] for row in tick_rows]
        immune = [row["immune"][run_idx] for row in tick_rows]
        healthy = [row["susceptible"][run_idx] for row in tick_rows]
        total = [row["total"][run_idx] for row in tick_rows]
        weeks = [int(row["ticks"][run_idx]) for row in tick_rows]

        peak_idx = max(range(len(sick)), key=lambda idx: sick[idx])
        final_idx = len(sick) - 1
        summaries.append(
            RunSummary(
                peak_sick=sick[peak_idx],
                peak_week=weeks[peak_idx],
                final_sick=sick[final_idx],
                final_immune=immune[final_idx],
                final_healthy=healthy[final_idx],
                final_total=total[final_idx],
            )
        )
    return summaries

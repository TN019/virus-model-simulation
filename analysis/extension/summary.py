from __future__ import annotations

import statistics
from dataclasses import dataclass
from pathlib import Path

from analysis.common.spreadsheet import load_per_run_series, load_per_run_summaries
from scripts.common.run_metrics import is_behaviorspace_spreadsheet, load_extension_run_metrics

EXTENSION_LEVELS: tuple[tuple[str, float], ...] = (
    ("00", 0.0),
    ("01", 1.0),
    ("02", 2.0),
    ("05", 5.0),
    ("10", 10.0),
    ("25", 25.0),
)


@dataclass(frozen=True)
class ExtensionRunMetrics:
    reinfection_probability: float
    persistent_runs: int
    total_runs: int
    persistence_rate: float
    mean_time_to_extinction: float
    censored_runs: int
    final_infected_percent: str
    peak_infected_percent: str
    infection_burden: str
    immune_reinfections: str


def _mean_sd(values: list[float], *, digits: int = 1) -> str:
    if not values:
        return "—"
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return f"{mean:.{digits}f} ± {sd:.{digits}f}"


def _condition_name(csv_path: Path) -> str:
    stem = csv_path.stem.replace("_100_runs-spreadsheet", "")
    return stem.replace("Virus Extension ", "").lower()


def _csv_for_condition(data_dir: Path, condition_key: str) -> Path | None:
    for path in data_dir.glob("*.csv"):
        if not is_behaviorspace_spreadsheet(path):
            continue
        if _condition_name(path) == condition_key.lower():
            return path
    return None


def _time_to_extinction(infected: list[float], max_tick: int) -> int:
    for tick, count in enumerate(infected):
        if count == 0:
            return tick
    return max_tick


def _load_reinfection_counts(data_dir: Path, condition_key: str) -> list[int]:
    metrics = load_extension_run_metrics(data_dir, condition_key)
    if metrics is None:
        return []
    return list(metrics.immune_reinfections_per_run)


def load_mean_cumulative_reinfections(data_dir: Path, condition_key: str) -> tuple[list[int], list[float]]:
    metrics = load_extension_run_metrics(data_dir, condition_key)
    if metrics is None:
        return [], []

    by_run = metrics.cumulative_reinfections_by_run
    if not by_run:
        return [], []

    max_len = max(len(series) for series in by_run)
    weeks = list(range(max_len))
    means: list[float] = []
    for tick_idx in range(max_len):
        values = [series[tick_idx] for series in by_run if tick_idx < len(series)]
        means.append(statistics.mean(values) if values else 0.0)
    return weeks, means


def load_total_reinfections_by_probability(data_dir: Path) -> list[tuple[float, int]]:
    totals: list[tuple[float, int]] = []
    for condition_key, probability in EXTENSION_LEVELS:
        counts = _load_reinfection_counts(data_dir, condition_key)
        if not counts:
            continue
        totals.append((probability, sum(counts)))
    return totals


def summarize_extension_condition(data_dir: Path, condition_key: str, probability: float) -> ExtensionRunMetrics:
    csv_path = _csv_for_condition(data_dir, condition_key)
    if csv_path is None:
        raise FileNotFoundError(f"No CSV for {condition_key} in {data_dir}")

    run_series = load_per_run_series(csv_path)
    summaries = load_per_run_summaries(csv_path)
    total_runs = len(run_series)
    max_tick = max(int(series["ticks"][-1]) for series in run_series)

    persistent_runs = sum(1 for summary in summaries if summary.final_sick > 0)
    extinction_times: list[int] = []
    censored_runs = 0
    final_percents: list[float] = []
    peak_percents: list[float] = []
    burdens: list[float] = []

    for series in run_series:
        infected = series["infected"]
        percents = series["percent_infected"]
        extinction_tick = _time_to_extinction(infected, max_tick)
        extinction_times.append(extinction_tick)
        if extinction_tick == max_tick and all(count > 0 for count in infected):
            censored_runs += 1
        final_percents.append(percents[-1])
        peak_percents.append(max(percents))
        burdens.append(sum(infected))

    reinfection_counts = _load_reinfection_counts(data_dir, condition_key)

    return ExtensionRunMetrics(
        reinfection_probability=probability,
        persistent_runs=persistent_runs,
        total_runs=total_runs,
        persistence_rate=(persistent_runs / total_runs) * 100 if total_runs else 0.0,
        mean_time_to_extinction=statistics.mean(extinction_times) if extinction_times else 0.0,
        censored_runs=censored_runs,
        final_infected_percent=_mean_sd(final_percents),
        peak_infected_percent=_mean_sd(peak_percents),
        infection_burden=_mean_sd(burdens, digits=0),
        immune_reinfections=_mean_sd([float(value) for value in reinfection_counts], digits=0),
    )


def build_extension_metrics(data_dir: Path) -> list[ExtensionRunMetrics]:
    metrics: list[ExtensionRunMetrics] = []
    for condition_key, probability in EXTENSION_LEVELS:
        csv_path = _csv_for_condition(data_dir, condition_key)
        if csv_path is None:
            continue
        metrics.append(summarize_extension_condition(data_dir, condition_key, probability))
    return metrics


def render_persistence_table(rows: list[ExtensionRunMetrics]) -> str:
    lines = [
        "# Persistence probability",
        "",
        "| Reinfection Probability | Persistent Runs / 100 | Persistence Rate |",
        "| ----------------------: | --------------------: | ---------------: |",
    ]
    for row in rows:
        total = row.total_runs
        lines.append(
            f"| {row.reinfection_probability:.0f} | "
            f"{row.persistent_runs} / {total} | {row.persistence_rate:.1f}% |"
        )
    lines.append("")
    lines.append("_Persistent = final infected > 0 at the last tick._")
    lines.append("")
    return "\n".join(lines)


def render_secondary_metrics_table(rows: list[ExtensionRunMetrics]) -> str:
    lines = [
        "# Secondary metrics",
        "",
        "| Reinfection % | Mean time to extinction | Censored runs | Final infected % | Peak infected % | Infection burden | Immune reinfections |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row.reinfection_probability:.0f} | {row.mean_time_to_extinction:.1f} | "
            f"{row.censored_runs} | {row.final_infected_percent} | {row.peak_infected_percent} | "
            f"{row.infection_burden} | {row.immune_reinfections} |"
        )
    lines.append("")
    lines.append(
        "_Time to extinction = first tick with infected = 0; if never extinct, censored at max tick. "
        "Immune reinfections = mean ± SD per run from simulation counter._"
    )
    lines.append("")
    return "\n".join(lines)


def load_survival_curves(data_dir: Path) -> list[tuple[float, list[int], list[float]]]:
    curves: list[tuple[float, list[int], list[float]]] = []
    for condition_key, probability in EXTENSION_LEVELS:
        csv_path = _csv_for_condition(data_dir, condition_key)
        if csv_path is None:
            continue
        run_series = load_per_run_series(csv_path)
        max_tick = max(int(series["ticks"][-1]) for series in run_series)
        ticks = list(range(max_tick + 1))
        proportions: list[float] = []
        for tick in ticks:
            alive = sum(1 for series in run_series if series["infected"][tick] > 0)
            proportions.append(alive / len(run_series))
        curves.append((probability, ticks, proportions))
    return curves

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

RUN_METRICS_SUFFIX = "_run_metrics.csv"


@dataclass(frozen=True)
class ExtensionRunMetricsData:
    condition: str
    immune_reinfection_probability: float
    ticks: int
    runs: int
    immune_reinfections_per_run: tuple[int, ...]
    cumulative_reinfections_by_run: tuple[tuple[int, ...], ...]


def run_metrics_path(output_dir: Path, condition: str) -> Path:
    return output_dir / f"{condition}{RUN_METRICS_SUFFIX}"


def is_run_metrics_csv(path: Path) -> bool:
    return path.name.endswith(RUN_METRICS_SUFFIX)


def is_behaviorspace_spreadsheet(path: Path) -> bool:
    return path.suffix.lower() == ".csv" and not is_run_metrics_csv(path)


def write_extension_run_metrics_csv(
    path: Path,
    *,
    condition: str,
    immune_reinfection_probability: float,
    ticks: int,
    runs: int,
    immune_reinfections_per_run: list[int],
    cumulative_reinfections_by_run: list[list[int]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tick_columns = [f"tick_{index}" for index in range(ticks)]

    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["section", "key", "value"])
        writer.writerow(["metadata", "condition", condition])
        writer.writerow(["metadata", "immune_reinfection_probability", immune_reinfection_probability])
        writer.writerow(["metadata", "ticks", ticks])
        writer.writerow(["metadata", "runs", runs])
        writer.writerow([])

        writer.writerow(["immune_reinfections_per_run", "run", "count"])
        for run_id, count in enumerate(immune_reinfections_per_run, start=1):
            writer.writerow(["immune_reinfections_per_run", run_id, count])
        writer.writerow([])

        writer.writerow(["cumulative_reinfections_by_run", "run", *tick_columns])
        for run_id, series in enumerate(cumulative_reinfections_by_run, start=1):
            writer.writerow(["cumulative_reinfections_by_run", run_id, *series])


def load_extension_run_metrics_csv(path: Path) -> ExtensionRunMetricsData:
    metadata: dict[str, str] = {}
    immune_reinfections_per_run: list[int] = []
    cumulative_reinfections_by_run: list[list[int]] = []
    current_section: str | None = None

    with path.open(newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if not row:
                current_section = None
                continue

            section = row[0]
            if section == "section":
                continue
            if section == "metadata" and len(row) >= 3:
                metadata[row[1]] = row[2]
                continue
            if section == "immune_reinfections_per_run":
                if row[1] == "run":
                    current_section = section
                    continue
                if current_section == section and len(row) >= 3:
                    immune_reinfections_per_run.append(int(row[2]))
                continue
            if section == "cumulative_reinfections_by_run":
                if row[1] == "run":
                    current_section = section
                    continue
                if current_section == section and len(row) >= 3:
                    cumulative_reinfections_by_run.append([int(value) for value in row[2:]])

    return ExtensionRunMetricsData(
        condition=metadata.get("condition", ""),
        immune_reinfection_probability=float(metadata.get("immune_reinfection_probability", 0)),
        ticks=int(metadata.get("ticks", 0)),
        runs=int(metadata.get("runs", 0)),
        immune_reinfections_per_run=tuple(immune_reinfections_per_run),
        cumulative_reinfections_by_run=tuple(tuple(series) for series in cumulative_reinfections_by_run),
    )


def _load_legacy_json_metrics(path: Path) -> ExtensionRunMetricsData:
    import json

    payload = json.loads(path.read_text())
    return ExtensionRunMetricsData(
        condition=str(payload.get("condition", "")),
        immune_reinfection_probability=float(payload.get("immune_reinfection_probability", 0)),
        ticks=int(payload.get("ticks", 0)),
        runs=int(payload.get("runs", 0)),
        immune_reinfections_per_run=tuple(int(v) for v in payload.get("immune_reinfections_per_run", [])),
        cumulative_reinfections_by_run=tuple(
            tuple(int(v) for v in series) for series in payload.get("cumulative_reinfections_by_run", [])
        ),
    )


def load_extension_run_metrics(data_dir: Path, condition_key: str) -> ExtensionRunMetricsData | None:
    csv_path = run_metrics_path(data_dir, condition_key)
    if csv_path.exists():
        return load_extension_run_metrics_csv(csv_path)

    json_path = data_dir / f"{condition_key}_run_metrics.json"
    if json_path.exists():
        return _load_legacy_json_metrics(json_path)

    return None

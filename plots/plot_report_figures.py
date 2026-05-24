from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

import matplotlib.pyplot as plt


ROOT = Path.cwd()
OUTPUT_DIR = ROOT / "plots" / "output"

LEVELS = ["00", "01", "02", "05", "10", "25"]
LEVEL_LABELS = {
    "00": "0%",
    "01": "1%",
    "02": "2%",
    "05": "5%",
    "10": "10%",
    "25": "25%",
}

CONDITION_ORDER = [
    "no_infection",
    "low_spread_high_recovery",
    "baseline",
    "full_infection",
    "high_spread_low_recovery",
]

CONDITION_LABELS = {
    "no_infection": "No infection",
    "low_spread_high_recovery": "Low spread\nhigh recovery",
    "baseline": "Baseline",
    "full_infection": "Full infection",
    "high_spread_low_recovery": "High spread\nlow recovery",
}

METRIC_LABELS = {
    "peak sick": "Peak infected population",
    "final sick": "Final infected population",
    "final immune": "Final immune population",
    "final total": "Final total population",
}

EXTENSION_ANALYSIS_FILES = {
    "52 ticks": ROOT / "analysis" / "results" / "extension" / "extension" / "secondary_metrics.md",
    "156 ticks": ROOT / "analysis" / "results" / "extension_156ticks" / "extension" / "secondary_metrics.md",
    "260 ticks": ROOT / "analysis" / "results" / "extension_260ticks" / "extension" / "secondary_metrics.md",
}

EXTENSION_DATA_DIRS = {
    "52 ticks": ROOT / "output" / "python_extension",
    "156 ticks": ROOT / "output" / "python_extension_156ticks",
    "260 ticks": ROOT / "output" / "python_extension_260ticks",
}


def clean_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in OUTPUT_DIR.iterdir():
        if path.suffix.lower() in {".png", ".md"}:
            path.unlink()


def normalise_text(value: str) -> str:
    return (
        value.replace("\ufeff", "")
        .replace("\u00a0", " ")
        .strip()
        .strip('"')
        .strip("'")
        .lower()
    )


def safe_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).replace(",", "").strip().strip('"').strip("'")
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_mean_sd(value: str) -> tuple[float, float]:
    """Parse cells like '23.7 ± 6.9', '23.7 +/- 6.9', or '23.7'."""
    text = value.replace("±", "+/-").replace("−", "-").strip()
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    if not nums:
        return 0.0, 0.0
    if len(nums) == 1:
        return float(nums[0]), 0.0
    return float(nums[0]), float(nums[1])


def parse_markdown_table(path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    if not path.exists():
        return rows

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
        if re.fullmatch(r"\|[\s:\-\|]+\|", line):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and normalise_text(cells[0]) not in {"metric", "reinfection %", "condition", "horizon"}:
            rows.append(cells)
    return rows


def condition_key_from_filename(path: Path) -> str:
    name = path.stem.lower()
    name = name.replace("_summary", "")
    for key in CONDITION_ORDER:
        if key in name:
            return key
    return name


def read_all_replication_summaries() -> list[dict]:
    summary_dir = ROOT / "analysis" / "results" / "replication" / "comparison"
    rows: list[dict] = []

    if not summary_dir.exists():
        print(f"Missing replication summary directory: {summary_dir}")
        return rows

    for path in sorted(summary_dir.glob("*_summary.md")):
        condition = condition_key_from_filename(path)
        metrics: dict[str, dict] = {}
        for cells in parse_markdown_table(path):
            if len(cells) < 4:
                continue
            metric = normalise_text(cells[0])
            netlogo_mean, netlogo_sd = parse_mean_sd(cells[1])
            python_mean, python_sd = parse_mean_sd(cells[2])
            diff = safe_float(cells[3])
            if diff is None:
                diff = python_mean - netlogo_mean
            metrics[metric] = {
                "netlogo_mean": netlogo_mean,
                "netlogo_sd": netlogo_sd,
                "python_mean": python_mean,
                "python_sd": python_sd,
                "difference": diff,
            }

        if metrics:
            rows.append({"condition": condition, "metrics": metrics})

    order = {condition: i for i, condition in enumerate(CONDITION_ORDER)}
    rows.sort(key=lambda r: order.get(r["condition"], 999))
    return rows


def interpretation_for_differences(values: list[float]) -> str:
    max_abs = max(abs(v) for v in values) if values else 0.0
    if max_abs <= 3:
        return "Very close replication"
    if max_abs <= 8:
        return "Similar trend with moderate numerical difference"
    return "Same qualitative pattern but larger numerical difference"


def write_replication_summary_table(rows: list[dict]) -> None:
    lines = [
        "# Replication Summary Table",
        "",
        "Difference = Python mean - NetLogo mean.",
        "",
        "| Condition | Peak infected difference | Final infected difference | Final immune difference | Final total difference | Interpretation |",
        "|---|---:|---:|---:|---:|---|",
    ]

    table_for_png = [["Condition", "Peak diff", "Final infected diff", "Final immune diff", "Final total diff", "Interpretation"]]

    for row in rows:
        metrics = row["metrics"]
        diffs = [
            metrics.get("peak sick", {}).get("difference", 0.0),
            metrics.get("final sick", {}).get("difference", 0.0),
            metrics.get("final immune", {}).get("difference", 0.0),
            metrics.get("final total", {}).get("difference", 0.0),
        ]
        interpretation = interpretation_for_differences(diffs)
        condition_label = CONDITION_LABELS.get(row["condition"], row["condition"]).replace("\n", " ")
        lines.append(
            f"| {condition_label} | {diffs[0]:.1f} | {diffs[1]:.1f} | {diffs[2]:.1f} | {diffs[3]:.1f} | {interpretation} |"
        )
        table_for_png.append([condition_label, *(f"{d:.1f}" for d in diffs), interpretation])

    (OUTPUT_DIR / "replication_summary_table.md").write_text("\n".join(lines), encoding="utf-8")
    save_table_png(
        table_for_png,
        OUTPUT_DIR / "replication_summary_table.png",
        title="Replication summary table",
        column_widths=[0.17, 0.13, 0.18, 0.18, 0.16, 0.28],
        font_size=8,
    )


def plot_replication_difference_chart(rows: list[dict]) -> None:
    metrics = ["peak sick", "final sick", "final immune", "final total"]
    labels = ["Peak infected", "Final infected", "Final immune", "Final total"]

    x = list(range(len(rows)))
    width = 0.18

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, metric in enumerate(metrics):
        values = [row["metrics"].get(metric, {}).get("difference", 0.0) for row in rows]
        offsets = [v + (i - 1.5) * width for v in x]
        ax.bar(offsets, values, width=width, label=labels[i])

    ax.axhline(0, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([CONDITION_LABELS.get(row["condition"], row["condition"]) for row in rows])
    ax.set_xlabel("Replication condition")
    ax.set_ylabel("Difference (Python mean - NetLogo mean)")
    ax.set_title("Replication differences across conditions")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "replication_difference_bar_chart.png", dpi=300)
    plt.close(fig)


def plot_replication_metric_comparison(rows: list[dict], metric: str, filename: str) -> None:
    labels = [CONDITION_LABELS.get(row["condition"], row["condition"]) for row in rows]
    x = list(range(len(rows)))
    width = 0.36

    netlogo_means = [row["metrics"].get(metric, {}).get("netlogo_mean", 0.0) for row in rows]
    python_means = [row["metrics"].get(metric, {}).get("python_mean", 0.0) for row in rows]
    netlogo_sds = [row["metrics"].get(metric, {}).get("netlogo_sd", 0.0) for row in rows]
    python_sds = [row["metrics"].get(metric, {}).get("python_sd", 0.0) for row in rows]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([v - width / 2 for v in x], netlogo_means, width=width, yerr=netlogo_sds, capsize=4, label="NetLogo mean")
    ax.bar([v + width / 2 for v in x], python_means, width=width, yerr=python_sds, capsize=4, label="Python mean")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_xlabel("Replication condition")
    ax.set_ylabel(METRIC_LABELS.get(metric, metric))
    ax.set_title(f"Replication comparison: {METRIC_LABELS.get(metric, metric)}")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.5, 0.01, "Black error bars show +/- 1 standard deviation across simulation runs.", ha="center", fontsize=9)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close(fig)


def read_extension_metrics_from_file(path: Path, horizon: str) -> list[dict]:
    rows: list[dict] = []
    for cells in parse_markdown_table(path):
        if len(cells) < 7:
            continue
        reinfection = safe_float(cells[0])
        if reinfection is None:
            continue

        final_infected_mean, final_infected_sd = parse_mean_sd(cells[3])
        peak_infected_mean, peak_infected_sd = parse_mean_sd(cells[4])
        infection_burden_mean, infection_burden_sd = parse_mean_sd(cells[5])
        immune_reinfection_mean, immune_reinfection_sd = parse_mean_sd(cells[6])

        rows.append(
            {
                "horizon": horizon,
                "reinfection": reinfection,
                "level": f"{int(reinfection):02d}" if reinfection < 10 else str(int(reinfection)),
                "label": f"{int(reinfection)}%",
                "final_infected_mean": final_infected_mean,
                "final_infected_sd": final_infected_sd,
                "peak_infected_mean": peak_infected_mean,
                "peak_infected_sd": peak_infected_sd,
                "infection_burden_mean": infection_burden_mean,
                "infection_burden_sd": infection_burden_sd,
                "immune_reinfection_mean": immune_reinfection_mean,
                "immune_reinfection_sd": immune_reinfection_sd,
            }
        )

    rows.sort(key=lambda r: r["reinfection"])
    return rows


def read_all_extension_metrics() -> dict[str, list[dict]]:
    all_rows: dict[str, list[dict]] = {}
    for horizon, path in EXTENSION_ANALYSIS_FILES.items():
        if path.exists():
            rows = read_extension_metrics_from_file(path, horizon)
            if rows:
                all_rows[horizon] = rows
        else:
            print(f"Missing extension metrics file: {path}")
    return all_rows


def longest_available_horizon(all_rows: dict[str, list[dict]]) -> str | None:
    for horizon in ["260 ticks", "156 ticks", "52 ticks"]:
        if horizon in all_rows:
            return horizon
    return None


def write_extension_horizon_summary_table(all_rows: dict[str, list[dict]]) -> None:
    lines = [
        "# Extension Horizon Summary Table",
        "",
        "| Horizon | Reinfection % | Final infected mean (%) | Peak infected mean (%) | Infection burden mean | Immune reinfections mean |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    table_for_png = [["Horizon", "Reinfection %", "Final infected (%)", "Peak infected (%)", "Infection burden", "Immune reinfections"]]

    for horizon in ["52 ticks", "156 ticks", "260 ticks"]:
        for row in all_rows.get(horizon, []):
            lines.append(
                f"| {horizon} | {row['reinfection']:.0f} | {row['final_infected_mean']:.1f} | "
                f"{row['peak_infected_mean']:.1f} | {row['infection_burden_mean']:.1f} | "
                f"{row['immune_reinfection_mean']:.1f} |"
            )
            table_for_png.append(
                [
                    horizon,
                    f"{row['reinfection']:.0f}",
                    f"{row['final_infected_mean']:.1f}",
                    f"{row['peak_infected_mean']:.1f}",
                    f"{row['infection_burden_mean']:.1f}",
                    f"{row['immune_reinfection_mean']:.1f}",
                ]
            )

    (OUTPUT_DIR / "extension_horizon_summary_table.md").write_text("\n".join(lines), encoding="utf-8")
    save_table_png(
        table_for_png,
        OUTPUT_DIR / "extension_horizon_summary_table.png",
        title="Extension horizon summary table",
        column_widths=[0.12, 0.12, 0.18, 0.18, 0.20, 0.20],
        font_size=8,
    )


def plot_extension_bar_with_error(rows: list[dict], mean_key: str, sd_key: str, ylabel: str, title: str, filename: str) -> None:
    labels = [row["label"] for row in rows]
    means = [row[mean_key] for row in rows]
    sds = [row[sd_key] for row in rows]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(labels, means, yerr=sds, capsize=4)
    ax.set_xlabel("Immune reinfection probability")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.5, 0.01, "Black error bars show +/- 1 standard deviation across simulation runs.", ha="center", fontsize=9)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close(fig)


def plot_extension_horizon_lines(all_rows: dict[str, list[dict]], mean_key: str, ylabel: str, title: str, filename: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    for horizon in ["52 ticks", "156 ticks", "260 ticks"]:
        rows = all_rows.get(horizon, [])
        if not rows:
            continue
        x = [row["reinfection"] for row in rows]
        y = [row[mean_key] for row in rows]
        ax.plot(x, y, marker="o", label=horizon)

    ax.set_xlabel("Immune reinfection probability (%)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close(fig)


def save_table_png(table: list[list[str]], path: Path, title: str, column_widths: list[float], font_size: int = 8) -> None:
    if not table or len(table) < 2:
        return

    n_rows = len(table)
    fig_height = max(3.5, 0.35 * n_rows + 1.2)
    fig, ax = plt.subplots(figsize=(13, fig_height))
    ax.axis("off")
    ax.set_title(title, fontsize=16, fontweight="bold", pad=14)

    mpl_table = ax.table(
        cellText=table[1:],
        colLabels=table[0],
        loc="center",
        cellLoc="left",
        colLoc="left",
        colWidths=column_widths,
    )
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)
    mpl_table.scale(1, 1.35)

    for (row, col), cell in mpl_table.get_celld().items():
        if row == 0:
            cell.set_text_props(fontweight="bold")
        if col > 0 and row > 0:
            cell.set_text_props(ha="right")

    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def is_run_header(value: str) -> bool:
    text = normalise_text(value)
    return text in {"[run number]", "run number", "run", "run_id", "run id"}


def is_sick_count_header(value: str) -> bool:
    text = normalise_text(value)
    if not text:
        return False

    if "%" in text or "percent" in text or "percentage" in text:
        return False
    if "not sick" in text or "not infected" in text:
        return False
    if "immune" in text or "healthy" in text or "total" in text:
        return False

    return (
        "count turtles with [sick" in text
        or text in {"sick", "infected", "sick people", "infected people", "sick count", "infected count"}
        or "count sick" in text
        or "count infected" in text
        or (("sick?" in text or "infected?" in text) and "not" not in text)
    )


def parse_horizontal_behaviorspace(rows: list[list[str]]) -> list[float]:
    """Read BehaviorSpace-style horizontal CSV: one sick-count column per run."""
    best_header_index: int | None = None
    best_sick_columns: list[int] = []

    for i, row in enumerate(rows):
        sick_columns = [j for j, cell in enumerate(row) if is_sick_count_header(cell)]
        if len(sick_columns) > len(best_sick_columns):
            best_header_index = i
            best_sick_columns = sick_columns

    if best_header_index is None or len(best_sick_columns) < 2:
        return []

    burdens: list[float] = []
    for col in best_sick_columns:
        values: list[float] = []
        for row in rows[best_header_index + 1 :]:
            if col >= len(row):
                continue
            value = safe_float(row[col])
            if value is not None:
                values.append(value)

        if values:
            burdens.append(sum(values))

    return burdens


def parse_vertical_behaviorspace(rows: list[list[str]]) -> list[float]:
    """Read vertical CSV: one row per run/tick and a run-number column."""
    best: tuple[int, int, int] | None = None

    for i, row in enumerate(rows):
        run_cols = [j for j, cell in enumerate(row) if is_run_header(cell)]
        sick_cols = [j for j, cell in enumerate(row) if is_sick_count_header(cell)]
        if run_cols and sick_cols:
            best = (i, run_cols[0], sick_cols[0])
            break

    if best is None:
        return []

    header_index, run_col, sick_col = best
    grouped: dict[str, float] = defaultdict(float)

    for row in rows[header_index + 1 :]:
        if run_col >= len(row) or sick_col >= len(row):
            continue
        run_value = str(row[run_col]).strip()
        sick_value = safe_float(row[sick_col])
        if run_value and sick_value is not None:
            grouped[run_value] += sick_value

    def sort_key(run_id: str) -> tuple[int, str]:
        numeric = safe_float(run_id)
        if numeric is None:
            return (10**9, run_id)
        return (int(numeric), run_id)

    return [grouped[key] for key in sorted(grouped, key=sort_key)]


def load_infection_burden_per_run(csv_path: Path) -> list[float]:
    rows = read_csv_rows(csv_path)

    horizontal = parse_horizontal_behaviorspace(rows)
    vertical = parse_vertical_behaviorspace(rows)

    # Choose the parser that found more runs. If tied, choose the one with larger mean,
    # because infection burden should be infected-count summed over ticks, not a percentage column.
    candidates = [values for values in [horizontal, vertical] if values]
    if not candidates:
        return []

    candidates.sort(key=lambda values: (len(values), mean(values)), reverse=True)
    return candidates[0]


def find_extension_csv(data_dir: Path, level: str) -> Path | None:
    if not data_dir.exists():
        return None

    exact_pattern = re.compile(rf"virus\s+extension\s+{re.escape(level)}_.*spreadsheet.*\.csv$", re.IGNORECASE)
    for path in data_dir.glob("*.csv"):
        if exact_pattern.search(path.name):
            return path

    # Fallback: choose a CSV containing the level and spreadsheet.
    candidates = [
        path for path in data_dir.glob("*.csv")
        if f"Extension {level}" in path.name and "spreadsheet" in path.name.lower()
    ]
    if candidates:
        return candidates[0]

    return None


def load_reinfections_per_run(data_dir: Path, level: str) -> list[float]:
    from scripts.common.run_metrics import load_extension_run_metrics

    metrics = load_extension_run_metrics(data_dir, level)
    if metrics is None:
        return []

    if metrics.immune_reinfections_per_run:
        return [float(value) for value in metrics.immune_reinfections_per_run]

    cumulative = metrics.cumulative_reinfections_by_run
    return [float(series[-1]) for series in cumulative if series]


def build_per_run_dataset(horizon: str, summary_rows: list[dict] | None = None) -> list[dict]:
    data_dir = EXTENSION_DATA_DIRS.get(horizon)
    if data_dir is None or not data_dir.exists():
        print(f"Missing data directory for {horizon}: {data_dir}")
        return []

    expected_by_level: dict[str, float] = {}
    for row in summary_rows or []:
        expected_by_level[row["level"]] = row["infection_burden_mean"]

    dataset: list[dict] = []

    for level in LEVELS:
        csv_path = find_extension_csv(data_dir, level)
        if csv_path is None:
            print(f"Missing CSV for level {level} in {data_dir}")
            continue

        burdens = load_infection_burden_per_run(csv_path)
        reinfections = load_reinfections_per_run(data_dir, level)

        if not burdens:
            print(f"Could not read infected-count burden for level {level} from {csv_path.name}")
            continue
        if not reinfections:
            print(f"Could not read reinfection metrics for level {level}")
            continue

        expected = expected_by_level.get(level)
        actual_mean = mean(burdens)
        if expected and expected > 0 and not (0.5 * expected <= actual_mean <= 1.5 * expected):
            print(
                f"Warning: parsed burden mean for level {level} is {actual_mean:.1f}, "
                f"but summary table mean is {expected:.1f}. Skipping this level to avoid a wrong figure."
            )
            continue

        n = min(len(burdens), len(reinfections))
        for i in range(n):
            dataset.append(
                {
                    "level": level,
                    "label": LEVEL_LABELS[level],
                    "reinfections": reinfections[i],
                    "infection_burden": burdens[i],
                }
            )

        print(
            f"Per-run infection burden check {LEVEL_LABELS[level]}: "
            f"n={n}, mean={mean(burdens[:n]):.1f}, min={min(burdens[:n]):.1f}, max={max(burdens[:n]):.1f}"
        )

    return dataset


def plot_per_run_distribution(dataset: list[dict], key: str, ylabel: str, title: str, filename: str) -> None:
    grouped: list[list[float]] = []
    labels: list[str] = []

    for level in LEVELS:
        values = [row[key] for row in dataset if row["level"] == level]
        if values:
            grouped.append(values)
            labels.append(LEVEL_LABELS[level])

    if not grouped:
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(grouped, labels=labels, showmeans=True)
    ax.set_xlabel("Immune reinfection probability")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.5, 0.01, "Boxplots show per-run distributions; triangle markers show run means.", ha="center", fontsize=9)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close(fig)


def plot_reinfections_vs_burden_scatter(dataset: list[dict]) -> None:
    if not dataset:
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    for level in LEVELS:
        rows = [row for row in dataset if row["level"] == level]
        if not rows:
            continue
        x = [row["reinfections"] for row in rows]
        y = [row["infection_burden"] for row in rows]
        ax.scatter(x, y, alpha=0.7, label=LEVEL_LABELS[level])

    ax.set_xlabel("Immune reinfection events per run")
    ax.set_ylabel("Infection burden (infected-person ticks per run)")
    ax.set_title("Per-run immune reinfections vs infection burden (260 ticks)")
    ax.legend(title="Immune reinfection probability")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "extension_reinfections_vs_infection_burden_scatter.png", dpi=300)
    plt.close(fig)


def plot_all_replication() -> None:
    rows = read_all_replication_summaries()
    if not rows:
        print("No replication summary data found.")
        return

    write_replication_summary_table(rows)
    plot_replication_difference_chart(rows)
    plot_replication_metric_comparison(rows, "peak sick", "replication_peak_sick_comparison.png")
    plot_replication_metric_comparison(rows, "final sick", "replication_final_sick_comparison.png")
    plot_replication_metric_comparison(rows, "final immune", "replication_final_immune_comparison.png")
    plot_replication_metric_comparison(rows, "final total", "replication_final_total_comparison.png")


def plot_all_extension() -> None:
    all_rows = read_all_extension_metrics()
    if not all_rows:
        print("No extension secondary metrics found. Run the extension analysis first.")
        return

    write_extension_horizon_summary_table(all_rows)

    horizon = longest_available_horizon(all_rows)
    if horizon is None:
        print("No extension horizon is available.")
        return

    print(f"Using longest available extension horizon: {horizon}")
    rows = all_rows[horizon]

    plot_extension_bar_with_error(
        rows,
        "final_infected_mean",
        "final_infected_sd",
        "Final infected population (%)",
        f"Final infected population by immune reinfection probability ({horizon})",
        "extension_final_infected_by_probability.png",
    )
    plot_extension_bar_with_error(
        rows,
        "peak_infected_mean",
        "peak_infected_sd",
        "Peak infected population (%)",
        f"Peak infected population by immune reinfection probability ({horizon})",
        "extension_peak_infected_by_probability.png",
    )
    plot_extension_bar_with_error(
        rows,
        "immune_reinfection_mean",
        "immune_reinfection_sd",
        "Immune reinfection events per run",
        f"Immune reinfections by immune reinfection probability ({horizon})",
        "extension_immune_reinfections_by_probability.png",
    )
    plot_extension_bar_with_error(
        rows,
        "infection_burden_mean",
        "infection_burden_sd",
        "Infection burden (infected-person ticks per run)",
        f"Infection burden by immune reinfection probability ({horizon})",
        "extension_infection_burden_by_probability.png",
    )

    plot_extension_horizon_lines(
        all_rows,
        "final_infected_mean",
        "Final infected population (%)",
        "Horizon comparison: final infected population",
        "extension_horizon_final_infected.png",
    )
    plot_extension_horizon_lines(
        all_rows,
        "immune_reinfection_mean",
        "Mean immune reinfection events per run",
        "Horizon comparison: immune reinfections",
        "extension_horizon_immune_reinfections.png",
    )
    plot_extension_horizon_lines(
        all_rows,
        "infection_burden_mean",
        "Mean infection burden (infected-person ticks per run)",
        "Horizon comparison: infection burden",
        "extension_horizon_infection_burden.png",
    )

    per_run_dataset = build_per_run_dataset("260 ticks", summary_rows=all_rows.get("260 ticks"))
    if per_run_dataset:
        plot_per_run_distribution(
            per_run_dataset,
            "infection_burden",
            "Infection burden (infected-person ticks per run)",
            "Per-run distribution of infection burden (260 ticks)",
            "extension_per_run_infection_burden_distribution.png",
        )
        plot_per_run_distribution(
            per_run_dataset,
            "reinfections",
            "Immune reinfection events per run",
            "Per-run distribution of immune reinfections (260 ticks)",
            "extension_per_run_reinfections_distribution.png",
        )
        plot_reinfections_vs_burden_scatter(per_run_dataset)
    else:
        print("No valid per-run dataset generated. The script did not create per-run distribution/scatter figures.")


def main() -> None:
    clean_output_dir()
    plot_all_replication()
    plot_all_extension()
    print(f"Generated final report figures in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

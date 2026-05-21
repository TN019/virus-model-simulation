from __future__ import annotations

from pathlib import Path
import re

import matplotlib.pyplot as plt


OUTPUT_DIR = Path("report_plots/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

POSSIBLE_METRICS_FILES = [
    Path("results/analysis/extension_260ticks/extension/secondary_metrics.md"),
    Path("results/analysis/extension_156ticks/extension/secondary_metrics.md"),
    Path("results/analysis/extension/extension/secondary_metrics.md"),
]

REPLICATION_DIR = Path("results/analysis/replication/comparison")


def find_metrics_file() -> Path:
    for path in POSSIBLE_METRICS_FILES:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Could not find secondary_metrics.md. "
        "Please run: uv run python -m run.plot_extension"
    )


def horizon_label(path: Path) -> str:
    text = str(path)
    if "260ticks" in text:
        return "260-tick"
    if "156ticks" in text:
        return "156-tick"
    return "52-tick"


def parse_mean_sd(value: str) -> tuple[float, float]:
    value = value.strip()
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*±\s*(-?\d+(?:\.\d+)?)", value)
    if match:
        return float(match.group(1)), float(match.group(2))

    nums = re.findall(r"-?\d+(?:\.\d+)?", value)
    if nums:
        return float(nums[0]), 0.0

    return 0.0, 0.0


def read_secondary_metrics(path: Path) -> list[dict]:
    rows = []

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line.startswith("|"):
            continue
        if "---" in line:
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]

        if not cells:
            continue
        if cells[0].lower().startswith("reinfection"):
            continue
        if len(cells) < 7:
            continue

        try:
            reinfection = float(cells[0])
        except ValueError:
            continue

        final_infected_mean, final_infected_sd = parse_mean_sd(cells[3])
        peak_infected_mean, peak_infected_sd = parse_mean_sd(cells[4])
        infection_burden_mean, infection_burden_sd = parse_mean_sd(cells[5])
        immune_reinfection_mean, immune_reinfection_sd = parse_mean_sd(cells[6])

        rows.append(
            {
                "reinfection": reinfection,
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

    if not rows:
        raise ValueError(f"No metric rows parsed from {path}")

    return rows


def plot_extension_bar_with_error(
    rows: list[dict],
    mean_key: str,
    sd_key: str,
    ylabel: str,
    title: str,
    filename: str,
    horizon: str,
) -> None:
    labels = [row["label"] for row in rows]
    means = [row[mean_key] for row in rows]
    errors = [row[sd_key] for row in rows]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, means, yerr=errors, capsize=4)
    plt.xlabel("Immune reinfection probability")
    plt.ylabel(ylabel)
    plt.title(f"{title} ({horizon} extension experiment)")
    plt.grid(axis="y", alpha=0.25)
    plt.figtext(
        0.5,
        0.01,
        "Black error bars show ±1 standard deviation across simulation runs.",
        ha="center",
        fontsize=9,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 1))
    plt.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close()


def plot_extension_line(
    rows: list[dict],
    mean_key: str,
    ylabel: str,
    title: str,
    filename: str,
    horizon: str,
) -> None:
    labels = [row["label"] for row in rows]
    values = [row[mean_key] for row in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(labels, values, marker="o")
    plt.xlabel("Immune reinfection probability")
    plt.ylabel(ylabel)
    plt.title(f"{title} ({horizon} extension experiment)")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close()


def condition_label_from_file(path: Path) -> str:
    name = path.stem.replace("_summary", "")

    labels = {
        "baseline": "Baseline",
        "no_infection": "No infection",
        "full_infection": "Full infection",
        "low_spread_high_recovery": "Low spread\nhigh recovery",
        "high_spread_low_recovery": "High spread\nlow recovery",
    }

    return labels.get(name, name.replace("_", " ").title())


def condition_order_key(path: Path) -> int:
    name = path.stem.replace("_summary", "")
    order = {
        "no_infection": 0,
        "low_spread_high_recovery": 1,
        "baseline": 2,
        "full_infection": 3,
        "high_spread_low_recovery": 4,
    }
    return order.get(name, 99)


def read_replication_summary(path: Path) -> dict[str, dict]:
    metrics = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line.startswith("|"):
            continue
        if "---" in line:
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]

        if len(cells) < 4:
            continue

        metric = cells[0].lower()

        if metric == "metric":
            continue

        netlogo_mean, netlogo_sd = parse_mean_sd(cells[1])
        python_mean, python_sd = parse_mean_sd(cells[2])

        metrics[metric] = {
            "netlogo_mean": netlogo_mean,
            "netlogo_sd": netlogo_sd,
            "python_mean": python_mean,
            "python_sd": python_sd,
        }

    return metrics


def read_all_replication_summaries() -> list[dict]:
    summary_files = sorted(
        REPLICATION_DIR.glob("*_summary.md"),
        key=condition_order_key,
    )

    rows = []

    for path in summary_files:
        metrics = read_replication_summary(path)
        if metrics:
            rows.append(
                {
                    "condition": condition_label_from_file(path),
                    "metrics": metrics,
                }
            )

    return rows


def plot_replication_metric(
    rows: list[dict],
    metric_name: str,
    ylabel: str,
    title: str,
    filename: str,
) -> None:
    valid_rows = [row for row in rows if metric_name in row["metrics"]]

    if not valid_rows:
        print(f"Skipping {filename}: metric not found: {metric_name}")
        return

    labels = [row["condition"] for row in valid_rows]

    netlogo_means = [row["metrics"][metric_name]["netlogo_mean"] for row in valid_rows]
    netlogo_sds = [row["metrics"][metric_name]["netlogo_sd"] for row in valid_rows]
    python_means = [row["metrics"][metric_name]["python_mean"] for row in valid_rows]
    python_sds = [row["metrics"][metric_name]["python_sd"] for row in valid_rows]

    x = list(range(len(valid_rows)))
    width = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar(
        [i - width / 2 for i in x],
        netlogo_means,
        width,
        yerr=netlogo_sds,
        capsize=4,
        label="NetLogo mean",
    )
    plt.bar(
        [i + width / 2 for i in x],
        python_means,
        width,
        yerr=python_sds,
        capsize=4,
        label="Python mean",
    )

    plt.xticks(x, labels)
    plt.xlabel("Replication condition")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    plt.figtext(
        0.5,
        0.01,
        "Black error bars show ±1 standard deviation across simulation runs.",
        ha="center",
        fontsize=9,
    )
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    plt.savefig(OUTPUT_DIR / filename, dpi=300)
    plt.close()


def main() -> None:
    metrics_file = find_metrics_file()
    horizon = horizon_label(metrics_file)
    extension_rows = read_secondary_metrics(metrics_file)

    print(f"Using extension metrics file: {metrics_file}")

    plot_extension_bar_with_error(
        extension_rows,
        mean_key="final_infected_mean",
        sd_key="final_infected_sd",
        ylabel="Final infected people",
        title="Final infected people by reinfection probability",
        filename="final_infected_by_probability.png",
        horizon=horizon,
    )

    plot_extension_bar_with_error(
        extension_rows,
        mean_key="peak_infected_mean",
        sd_key="peak_infected_sd",
        ylabel="Peak infected people",
        title="Peak infected people by reinfection probability",
        filename="peak_infected_by_probability.png",
        horizon=horizon,
    )

    plot_extension_line(
        extension_rows,
        mean_key="infection_burden_mean",
        ylabel="Infection burden",
        title="Infection burden by reinfection probability",
        filename="infection_burden_by_probability.png",
        horizon=horizon,
    )

    plot_extension_bar_with_error(
        extension_rows,
        mean_key="immune_reinfection_mean",
        sd_key="immune_reinfection_sd",
        ylabel="Immune reinfections per run",
        title="Immune reinfections by reinfection probability",
        filename="immune_reinfections_by_probability.png",
        horizon=horizon,
    )

    replication_rows = read_all_replication_summaries()

    if replication_rows:
        plot_replication_metric(
            replication_rows,
            metric_name="peak sick",
            ylabel="Peak sick people",
            title="Replication summary: peak sick people",
            filename="replication_peak_sick_comparison.png",
        )

        plot_replication_metric(
            replication_rows,
            metric_name="final sick",
            ylabel="Final sick people",
            title="Replication summary: final sick people",
            filename="replication_final_sick_comparison.png",
        )
    else:
        print(
            "No replication summary files found. "
            "Run: uv run python -m run.plot_figures"
        )

    print(f"Generated report figures in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
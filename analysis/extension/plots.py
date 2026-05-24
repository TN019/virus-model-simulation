from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from analysis.common.plots import (
    COMPARE_PANELS,
    FIGURE_DPI,
    align_tick_stats,
    plot_mean_line,
)
from analysis.common.spreadsheet import TickStats, load_tick_stats
from scripts.common.run_metrics import is_behaviorspace_spreadsheet
from analysis.common.paths import extension_aggregate, extension_condition
from analysis.extension.summary import (
    build_extension_metrics,
    load_mean_cumulative_reinfections,
    load_survival_curves,
    load_total_reinfections_by_probability,
    render_persistence_table,
    render_secondary_metrics_table,
)

CONDITION_STYLE: tuple[tuple[str, str, str], ...] = (
    ("00", "0% control", "tab:gray"),
    ("01", "1%", "tab:olive"),
    ("02", "2%", "tab:green"),
    ("05", "5%", "tab:orange"),
    ("10", "10%", "tab:red"),
    ("25", "25% (stress test)", "tab:purple"),
)

SURVIVAL_COLORS = {
    0.0: "tab:gray",
    1.0: "tab:olive",
    2.0: "tab:green",
    5.0: "tab:orange",
    10.0: "tab:red",
    25.0: "tab:purple",
}

POPULATION_COMPARE_PANELS = (
    ("sick", "Sick people"),
    ("immune", "Immune people"),
    ("healthy", "Healthy people"),
)


def _condition_name(csv_path: Path) -> str:
    stem = csv_path.stem.replace("_100_runs-spreadsheet", "")
    return stem.replace("Virus Extension ", "").lower()


def _safe_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("/", "_")


def plot_extension_trend_with_reinfections(
    csv_path: Path,
    data_dir: Path,
    output_path: Path,
    *,
    title: str,
) -> Path:
    condition = _condition_name(csv_path)
    stats = load_tick_stats(csv_path)
    weeks, cumulative = load_mean_cumulative_reinfections(data_dir, condition)

    fig, axes = plt.subplots(2, 1, figsize=(10, 9), sharex=True)

    for attr, label, color in (
        ("sick", "sick", "tab:red"),
        ("immune", "immune", "tab:gray"),
        ("healthy", "healthy", "tab:green"),
        ("total", "total", "tab:blue"),
    ):
        band = getattr(stats, attr)
        axes[0].plot(stats.tick, band.mean, label=label, color=color, linewidth=1.8)

    axes[0].set_title(title)
    axes[0].set_ylabel("Number of people")
    axes[0].legend(loc="upper right", fontsize=9)
    axes[0].grid(True, alpha=0.3)

    if weeks and cumulative:
        axes[1].plot(weeks, cumulative, color="tab:purple", linewidth=1.8)
    axes[1].set_xlabel("Week")
    axes[1].set_ylabel("Cumulative immune reinfection events")
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)
    return output_path


def plot_all_extension_trends(
    data_dir: Path,
    analysis_dir: Path,
    *,
    ticks: int | None = None,
) -> list[Path]:
    paths: list[Path] = []
    for csv_path in sorted(data_dir.glob("*.csv")):
        if not is_behaviorspace_spreadsheet(csv_path):
            continue
        condition = _condition_name(csv_path)
        label = next((display for key, display, _ in CONDITION_STYLE if key == condition), condition)
        out = extension_condition(analysis_dir, condition, ticks=ticks) / "trends.png"
        plot_extension_trend_with_reinfections(
            csv_path,
            data_dir,
            out,
            title=f"Extension — {label}",
        )
        paths.append(out)
    return paths


def plot_total_reinfections_by_probability(data_dir: Path, output_path: Path) -> Path:
    totals = load_total_reinfections_by_probability(data_dir)
    if not totals:
        raise ValueError(f"No reinfection metrics found in {data_dir}")

    probabilities = [item[0] for item in totals]
    counts = [item[1] for item in totals]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(probabilities, counts, marker="o", color="tab:purple", linewidth=1.8)
    ax.set_title("Extension — total immune reinfections across all runs")
    ax.set_xlabel("Reinfection probability")
    ax.set_ylabel("Total reinfections (all runs)")
    ax.set_xticks(probabilities)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)
    return output_path


def _load_condition_stats(data_dir: Path) -> list[tuple[str, str, str, TickStats]]:
    by_condition = {_condition_name(path): path for path in data_dir.glob("*.csv")}
    loaded: list[tuple[str, str, str, TickStats]] = []
    for key, label, color in CONDITION_STYLE:
        csv_path = by_condition.get(key)
        if csv_path is None:
            continue
        loaded.append((key, label, color, load_tick_stats(csv_path)))
    return loaded


def _load_aligned_cumulative_curves(
    data_dir: Path,
) -> tuple[list[int], list[tuple[str, str, list[float]]]]:
    curves: list[tuple[str, str, list[int], list[float]]] = []
    for key, label, color in CONDITION_STYLE:
        weeks, means = load_mean_cumulative_reinfections(data_dir, key)
        if not weeks:
            continue
        curves.append((label, color, weeks, means))

    if not curves:
        return [], []

    common_len = min(len(item[3]) for item in curves)
    weeks = list(range(common_len))
    aligned = [(label, color, means[:common_len]) for label, color, _, means in curves]
    return weeks, aligned


def plot_extension_conditions_compare(data_dir: Path, output_path: Path) -> Path:
    series = _load_condition_stats(data_dir)
    if len(series) < 2:
        raise ValueError(f"Need at least two extension CSV files in {data_dir}")

    ticks = series[0][3].tick
    aligned: list[tuple[str, str, str, TickStats]] = [series[0]]
    for key, label, color, stats in series[1:]:
        common_ticks, base_stats, stats = align_tick_stats(aligned[0][3], stats)
        ticks = common_ticks
        aligned[0] = (aligned[0][0], aligned[0][1], aligned[0][2], base_stats)
        aligned.append((key, label, color, stats))

    cumulative_weeks, cumulative_series = _load_aligned_cumulative_curves(data_dir)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True)

    for ax, (attr, ylabel) in zip(axes.flat[:3], POPULATION_COMPARE_PANELS, strict=True):
        for _, label, color, stats in aligned:
            band = getattr(stats, attr)
            ax.plot(ticks, band.mean, label=label, color=color, linewidth=1.8)
        ax.set_title(ylabel)
        ax.set_ylabel("Number of people")
        ax.legend(loc="best", fontsize=6)
        ax.grid(True, alpha=0.3)

    ax_cumulative = axes[1, 1]
    if cumulative_weeks and cumulative_series:
        for label, color, means in cumulative_series:
            ax_cumulative.plot(
                cumulative_weeks,
                means,
                label=label,
                color=color,
                linewidth=1.8,
            )
    ax_cumulative.set_title("Cumulative reinfections")
    ax_cumulative.set_ylabel("Cumulative immune reinfection events")
    ax_cumulative.legend(loc="best", fontsize=6)
    ax_cumulative.grid(True, alpha=0.3)

    for ax in axes[1]:
        ax.set_xlabel("Week")

    fig.suptitle("Extension — reinfection level comparison", y=1.02)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_infection_survival_curve(data_dir: Path, output_path: Path) -> Path:
    curves = load_survival_curves(data_dir)
    if not curves:
        raise ValueError(f"No survival curves could be built from {data_dir}")

    fig, ax = plt.subplots(figsize=(10, 6))
    for probability, ticks, proportions in curves:
        ax.plot(
            ticks,
            proportions,
            label=f"{probability:.0f}% reinfection",
            color=SURVIVAL_COLORS.get(probability, None),
            linewidth=1.8,
        )

    ax.set_title("Extension — proportion of runs with infection present")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Proportion of runs (infected > 0)")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)
    return output_path


def plot_extension_panels_by_metric(data_dir: Path, output_dir: Path) -> list[Path]:
    series = _load_condition_stats(data_dir)
    if not series:
        return []

    ticks = series[0][3].tick
    aligned: list[tuple[str, str, str, TickStats]] = [series[0]]
    for key, label, color, stats in series[1:]:
        common_ticks, base_stats, stats = align_tick_stats(aligned[0][3], stats)
        ticks = common_ticks
        aligned[0] = (aligned[0][0], aligned[0][1], aligned[0][2], base_stats)
        aligned.append((key, label, color, stats))

    paths: list[Path] = []
    for _, attr, ylabel in COMPARE_PANELS:
        fig, ax = plt.subplots(figsize=(10, 5))
        for _, label, color, stats in aligned:
            plot_mean_line(ax, ticks, getattr(stats, attr), label=label, color=color)
        ax.set_title(f"Extension — {ylabel}")
        ax.set_xlabel("Week")
        ax.set_ylabel("Number of people")
        ax.legend(loc="best", fontsize=7)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        out = output_dir / f"{attr}_by_reinfection.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=FIGURE_DPI)
        plt.close(fig)
        paths.append(out)
    return paths


def run_extension_analysis(data_dir: Path, analysis_dir: Path, *, ticks: int | None = None) -> list[Path]:
    written: list[Path] = []
    experiment_dir = extension_aggregate(analysis_dir, ticks=ticks)

    written.extend(plot_all_extension_trends(data_dir, analysis_dir, ticks=ticks))
    written.append(
        plot_extension_conditions_compare(
            data_dir,
            experiment_dir / "reinfection_levels_compare.png",
        )
    )
    written.extend(plot_extension_panels_by_metric(data_dir, experiment_dir))
    written.append(
        plot_infection_survival_curve(
            data_dir,
            experiment_dir / "infection_survival_curve.png",
        )
    )
    written.append(
        plot_total_reinfections_by_probability(
            data_dir,
            experiment_dir / "total_reinfections_by_probability.png",
        )
    )

    metrics = build_extension_metrics(data_dir)
    experiment_dir.mkdir(parents=True, exist_ok=True)
    persistence_path = experiment_dir / "persistence.md"
    persistence_path.write_text(render_persistence_table(metrics))
    written.append(persistence_path)

    secondary_path = experiment_dir / "secondary_metrics.md"
    secondary_path.write_text(render_secondary_metrics_table(metrics))
    written.append(secondary_path)

    return written

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from analysis.replication.summary import build_summary_rows, render_summary_markdown
from analysis.common.plots import (
    COMPARE_PANELS,
    FIGURE_DPI,
    align_tick_stats,
    plot_population_trends,
)
from analysis.common.spreadsheet import load_tick_stats


def _condition_name(csv_path: Path) -> str:
    stem = csv_path.stem.replace("_100_runs-spreadsheet", "")
    for prefix in ("Virus Extension ", "Virus "):
        if stem.startswith(prefix):
            return stem[len(prefix) :]
    return stem


def _safe_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("/", "_")


def plot_replication_compare(
    python_csv: Path,
    netlogo_csv: Path,
    output_path: Path,
    *,
    title: str,
) -> Path:
    python_stats = load_tick_stats(python_csv)
    netlogo_stats = load_tick_stats(netlogo_csv)
    ticks, python_stats, netlogo_stats = align_tick_stats(python_stats, netlogo_stats)
    if not ticks:
        raise ValueError(f"No overlapping ticks between {python_csv} and {netlogo_csv}")

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True)
    axes_flat = axes.flatten()

    for ax, (panel, attr, ylabel) in zip(axes_flat, COMPARE_PANELS, strict=True):
        py_band = getattr(python_stats, attr)
        nl_band = getattr(netlogo_stats, attr)
        ax.plot(ticks, nl_band.mean, label="NetLogo mean", color="tab:orange", linewidth=1.8)
        ax.plot(ticks, py_band.mean, label="Python mean", color="tab:blue", linewidth=1.8)
        ax.set_title(f"Panel {panel}: {ylabel}")
        ax.set_ylabel(ylabel)
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)

    for ax in axes[1]:
        ax.set_xlabel("Week")

    fig.suptitle(title, y=1.02)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=FIGURE_DPI, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_all_source(
    data_dir: Path,
    output_dir: Path,
    *,
    source_label: str,
) -> list[Path]:
    paths: list[Path] = []
    for csv_path in sorted(data_dir.glob("*.csv")):
        condition = _condition_name(csv_path)
        out = output_dir / f"{_safe_name(condition)}.png"
        plot_population_trends(csv_path, out, title=f"{source_label} {condition}")
        paths.append(out)
    return paths


def plot_all_replication(
    python_dir: Path,
    netlogo_dir: Path,
    output_dir: Path,
) -> tuple[list[Path], list[Path]]:
    figure_paths: list[Path] = []
    summary_paths: list[Path] = []

    for python_csv in sorted(python_dir.glob("*.csv")):
        netlogo_csv = netlogo_dir / python_csv.name
        if not netlogo_csv.exists():
            continue
        condition = _condition_name(python_csv)
        safe = _safe_name(condition)
        figure_paths.append(
            plot_replication_compare(
                python_csv,
                netlogo_csv,
                output_dir / f"{safe}_replication_compare.png",
                title=f"Replication compare — {condition}",
            )
        )
        rows = build_summary_rows(python_csv, netlogo_csv)
        summary_path = output_dir / f"{safe}_summary.md"
        summary_path.write_text(render_summary_markdown(rows, condition=condition))
        summary_paths.append(summary_path)

    return figure_paths, summary_paths

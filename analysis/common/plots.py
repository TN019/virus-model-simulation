from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from analysis.common.spreadsheet import TickStats, load_tick_stats

FIGURE_DPI = 150

SERIES_STYLE = (
    ("sick", "sick", "tab:red"),
    ("immune", "immune", "tab:gray"),
    ("healthy", "healthy", "tab:green"),
    ("total", "total", "tab:blue"),
)

COMPARE_PANELS = (
    ("A", "sick", "Sick people"),
    ("B", "immune", "Immune people"),
    ("C", "healthy", "Healthy people"),
    ("D", "total", "Total people"),
)


def align_tick_stats(left: TickStats, right: TickStats) -> tuple[list[int], TickStats, TickStats]:
    common_ticks = sorted(set(left.tick) & set(right.tick))
    left_index = {tick: idx for idx, tick in enumerate(left.tick)}
    right_index = {tick: idx for idx, tick in enumerate(right.tick)}

    def pick(stats: TickStats, index: dict[int, int]) -> TickStats:
        def slice_band(band_name: str):
            band = getattr(stats, band_name)
            return type(band)(
                mean=[band.mean[index[tick]] for tick in common_ticks],
                std=[band.std[index[tick]] for tick in common_ticks],
            )

        return TickStats(
            tick=common_ticks,
            sick=slice_band("sick"),
            immune=slice_band("immune"),
            healthy=slice_band("healthy"),
            total=slice_band("total"),
        )

    return common_ticks, pick(left, left_index), pick(right, right_index)


def plot_mean_line(ax, ticks: list[int], band, *, label: str, color: str) -> None:
    ax.plot(ticks, band.mean, label=label, color=color, linewidth=1.8)


def plot_population_trends(
    csv_path: Path,
    output_path: Path,
    *,
    title: str,
) -> Path:
    stats = load_tick_stats(csv_path)
    ticks = stats.tick

    fig, ax = plt.subplots(figsize=(10, 6))
    for attr, label, color in SERIES_STYLE:
        plot_mean_line(ax, ticks, getattr(stats, attr), label=label, color=color)

    ax.set_title(title)
    ax.set_xlabel("Week")
    ax.set_ylabel("Number of people")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)
    return output_path

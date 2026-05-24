from __future__ import annotations

import argparse
from pathlib import Path

from analysis.common.paths import DEFAULT_ANALYSIS, extension_aggregate
from analysis.extension.plots import (
    plot_all_extension_trends,
    plot_extension_conditions_compare,
    plot_infection_survival_curve,
    run_extension_analysis,
)
from analysis.extension.summary import (
    build_extension_metrics,
    render_persistence_table,
    render_secondary_metrics_table,
)

DEFAULT_DATA = Path("output/python_extension")


def _default_data_dir(ticks: int | None) -> Path:
    if ticks is None or ticks == 52:
        return DEFAULT_DATA
    return Path(f"output/python_extension_{ticks}ticks")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate extension experiment figures and summaries.")
    parser.add_argument(
        "--mode",
        choices=("trends", "compare", "survival", "summary", "all"),
        default="all",
    )
    parser.add_argument("--ticks", type=int, default=None, help="Match data folder horizon (52, 156, 260)")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS)
    args = parser.parse_args(argv)

    data_dir = args.data_dir or _default_data_dir(args.ticks)
    written: list[Path] = []

    if args.mode == "all":
        written.extend(run_extension_analysis(data_dir, args.analysis_dir, ticks=args.ticks))
    else:
        experiment_dir = extension_aggregate(args.analysis_dir, ticks=args.ticks)
        if args.mode == "trends":
            written.extend(plot_all_extension_trends(data_dir, args.analysis_dir, ticks=args.ticks))
        if args.mode == "compare":
            written.append(
                plot_extension_conditions_compare(
                    data_dir,
                    experiment_dir / "reinfection_levels_compare.png",
                )
            )
        if args.mode == "survival":
            written.append(
                plot_infection_survival_curve(
                    data_dir,
                    experiment_dir / "infection_survival_curve.png",
                )
            )
        if args.mode == "summary":
            metrics = build_extension_metrics(data_dir)
            experiment_dir.mkdir(parents=True, exist_ok=True)
            persistence_path = experiment_dir / "persistence.md"
            persistence_path.write_text(render_persistence_table(metrics))
            secondary_path = experiment_dir / "secondary_metrics.md"
            secondary_path.write_text(render_secondary_metrics_table(metrics))
            written.extend([persistence_path, secondary_path])

    print(f"Wrote {len(written)} file(s)")
    for path in written:
        print(f"  {path}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path

from analysis.plots import plot_all_replication, plot_all_source

DEFAULT_PYTHON_BASELINE = Path("results/data/python_baseline")
DEFAULT_NETLOGO_BASELINE = Path("results/data/netlogo_baseline")
DEFAULT_ANALYSIS = Path("results/analysis")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate replication analysis figures.")
    parser.add_argument(
        "--mode",
        choices=("netlogo", "python", "compare", "all"),
        default="all",
        help="Which outputs to generate",
    )
    parser.add_argument("--python-baseline-dir", type=Path, default=DEFAULT_PYTHON_BASELINE)
    parser.add_argument("--netlogo-baseline-dir", type=Path, default=DEFAULT_NETLOGO_BASELINE)
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS)
    args = parser.parse_args(argv)

    written: list[Path] = []

    if args.mode in ("netlogo", "all"):
        written.extend(
            plot_all_source(
                args.netlogo_baseline_dir,
                args.analysis_dir / "netlogo_baseline",
                source_label="NetLogo",
            )
        )

    if args.mode in ("python", "all"):
        written.extend(
            plot_all_source(
                args.python_baseline_dir,
                args.analysis_dir / "python_baseline",
                source_label="Python",
            )
        )

    if args.mode in ("compare", "all"):
        figures, summaries = plot_all_replication(
            args.python_baseline_dir,
            args.netlogo_baseline_dir,
            args.analysis_dir / "compare",
        )
        written.extend(figures)
        written.extend(summaries)

    print(f"Wrote {len(written)} file(s) to {args.analysis_dir}/")
    for path in written:
        print(f"  {path}")


if __name__ == "__main__":
    main()

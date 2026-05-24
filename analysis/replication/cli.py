from __future__ import annotations

import argparse
from pathlib import Path

from analysis.common.paths import (
    DEFAULT_ANALYSIS,
    replication_comparison,
    replication_netlogo,
    replication_python,
)
from analysis.replication.plots import plot_all_replication, plot_all_source

DEFAULT_PYTHON_DATA = Path("output/python_prototype")
DEFAULT_NETLOGO_DATA = Path("output/netlogo_prototype")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate replication analysis figures.")
    parser.add_argument(
        "--mode",
        choices=("netlogo", "python", "compare", "all"),
        default="all",
        help="Which outputs to generate",
    )
    parser.add_argument("--python-data-dir", type=Path, default=DEFAULT_PYTHON_DATA)
    parser.add_argument("--netlogo-data-dir", type=Path, default=DEFAULT_NETLOGO_DATA)
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS)
    args = parser.parse_args(argv)

    written: list[Path] = []

    if args.mode in ("netlogo", "all"):
        written.extend(
            plot_all_source(
                args.netlogo_data_dir,
                replication_netlogo(args.analysis_dir),
                source_label="NetLogo",
            )
        )

    if args.mode in ("python", "all"):
        written.extend(
            plot_all_source(
                args.python_data_dir,
                replication_python(args.analysis_dir),
                source_label="Python",
            )
        )

    if args.mode in ("compare", "all"):
        figures, summaries = plot_all_replication(
            args.python_data_dir,
            args.netlogo_data_dir,
            replication_comparison(args.analysis_dir),
        )
        written.extend(figures)
        written.extend(summaries)

    print(f"Wrote {len(written)} file(s) under {args.analysis_dir / 'replication'}/")
    for path in written:
        print(f"  {path}")


if __name__ == "__main__":
    main()

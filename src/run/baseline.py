from __future__ import annotations

import argparse
from pathlib import Path

from run.conditions import DEFAULT_BASELINE_DIR, load_conditions
from run.console import print_header
from run.runner import run_all

DEFAULT_OUTPUT = Path("results/data/python_baseline")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run baseline replication experiments.")
    parser.add_argument("--config-dir", type=Path, default=DEFAULT_BASELINE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--runs", type=int, default=None, help="Override runs from config files")
    parser.add_argument("--ticks", type=int, default=None, help="Override ticks from config files")
    parser.add_argument("--seed", type=int, default=None, help="Override base seed from config files")
    args = parser.parse_args(argv)

    conditions = load_conditions(args.config_dir)
    print_header("Replication Experiment")

    run_all(
        conditions,
        output_dir=args.output_dir,
        runs=args.runs,
        ticks=args.ticks,
        base_seed=args.seed,
    )


if __name__ == "__main__":
    main()

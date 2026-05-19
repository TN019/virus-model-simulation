from __future__ import annotations

import sys
from datetime import datetime, timezone


def print_header(title: str) -> None:
    now = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    print(title)
    print(f"Time: {now}")
    print()


def print_condition_start(name: str, run_index: int, total_runs: int) -> None:
    print(f"[{name}] run {run_index + 1}/{total_runs}", flush=True)


def print_condition_done(name: str, output_path: str) -> None:
    print(f"[{name}] wrote {output_path}", flush=True)


def eprint(message: str) -> None:
    print(message, file=sys.stderr)

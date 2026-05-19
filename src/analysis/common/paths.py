from __future__ import annotations

from pathlib import Path

DEFAULT_ANALYSIS = Path("results/analysis")


def replication_netlogo(analysis_dir: Path) -> Path:
    return analysis_dir / "replication" / "netlogo"


def replication_python(analysis_dir: Path) -> Path:
    return analysis_dir / "replication" / "python"


def replication_comparison(analysis_dir: Path) -> Path:
    return analysis_dir / "replication" / "comparison"


def extension_root(analysis_dir: Path, *, ticks: int | None = None) -> Path:
    if ticks is None or ticks == 52:
        return analysis_dir / "extension"
    return analysis_dir / f"extension_{ticks}ticks"


def extension_condition(analysis_dir: Path, condition: str, *, ticks: int | None = None) -> Path:
    return extension_root(analysis_dir, ticks=ticks) / condition


def extension_aggregate(analysis_dir: Path, *, ticks: int | None = None) -> Path:
    return extension_root(analysis_dir, ticks=ticks) / "extension"

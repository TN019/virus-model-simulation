from pathlib import Path

from analysis.summary import build_summary_rows, render_summary_markdown

NETLOGO = Path("results/data/netlogo_baseline/Virus Baseline_100_runs-spreadsheet.csv")
PYTHON = Path("results/data/python_baseline/Virus Baseline_100_runs-spreadsheet.csv")


def test_build_summary_markdown() -> None:
    if not NETLOGO.exists() or not PYTHON.exists():
        return
    rows = build_summary_rows(PYTHON, NETLOGO)
    assert len(rows) == 6
    md = render_summary_markdown(rows, condition="Baseline")
    assert "peak sick" in md
    assert "NetLogo mean ± SD" in md

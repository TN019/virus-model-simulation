from pathlib import Path

from analysis.spreadsheet import load_tick_series

NETLOGO = Path("results/data/netlogo_baseline/Virus Baseline_100_runs-spreadsheet.csv")


def test_load_netlogo_baseline_series() -> None:
    if not NETLOGO.exists():
        return
    series = load_tick_series(NETLOGO)
    assert len(series.tick) == 53
    assert series.tick[0] == 0
    assert series.tick[-1] == 52
    assert series.percent_infected[0] > 0

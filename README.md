# Virus Model Simulation

Python replication of the [NetLogo Virus model](https://ccl.northwestern.edu/netlogo/models/Virus) (SWEN90004 Assignment 2).

## Prerequisites

- [Python 3.14+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (`pip install uv` or the installer from the uv docs)

Commands below work the same on macOS, Linux, and Windows (PowerShell or Command Prompt). Run them from the project root.

## 1. Install dependencies

```bash
uv sync --extra dev --extra analysis
```

## 2. Add NetLogo reference data (for comparison)

Export BehaviorSpace spreadsheets from NetLogo and place them in:

`results/data/netlogo_baseline/`

Expected filenames (one per baseline condition), for example:

- `Virus Baseline_100_runs-spreadsheet.csv`
- `Virus No_infection_100_runs-spreadsheet.csv`
- `Virus Full_infection_100_runs-spreadsheet.csv`
- `Virus Low_spread_high_recovery_100_runs-spreadsheet.csv`
- `Virus High_spread_low_recovery_100_runs-spreadsheet.csv`

Skip this step if you only need Python-only plots (`--mode python`).

## 3. Run Python baseline experiments

Default: **100 runs × 52 ticks** per condition in `configs/baseline/`.

```bash
uv run python scripts/run_baseline.py
```

CSV output:

`results/data/python_baseline/`

Quick test (much faster):

```bash
uv run python scripts/run_baseline.py --runs 2 --ticks 10
```

## 4. Generate figures and comparison tables

```bash
uv run python scripts/plot_figures.py
```

## Final outputs

| Output | Location |
|--------|----------|
| Python experiment CSVs | `results/data/python_baseline/` |
| NetLogo reference CSVs | `results/data/netlogo_baseline/` |
| NetLogo trend plots | `results/analysis/netlogo_baseline/*.png` |
| Python trend plots | `results/analysis/python_baseline/*.png` |
| Python vs NetLogo (4 panels) | `results/analysis/compare/*_replication_compare.png` |
| Summary tables | `results/analysis/compare/*_summary.md` |

Plot only one part if needed:

```bash
uv run python scripts/plot_figures.py --mode netlogo
uv run python scripts/plot_figures.py --mode python
uv run python scripts/plot_figures.py --mode compare
```

## End-to-end (copy-paste)

```bash
uv sync --extra dev --extra analysis
uv run python scripts/run_baseline.py
uv run python scripts/plot_figures.py
```

After step 2 (NetLogo CSVs in place), step 4 also produces comparison plots and markdown summaries.

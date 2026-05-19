# Virus Model Simulation

Python replication of the [NetLogo Virus model](https://ccl.northwestern.edu/netlogo/models/Virus) (SWEN90004 Assignment 2).

## Prerequisites

- [Python 3.14+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (`pip install uv` or the installer from the uv docs)

Commands below work the same on macOS, Linux, and Windows (PowerShell or Command Prompt). Run them from the project root.

## 1. Install dependencies

```bash
uv sync --extra analysis
```

## 2. Add NetLogo reference data (for comparison)

Export BehaviorSpace spreadsheets from NetLogo and place them in:

`results/data/netlogo_prototype/`

Expected filenames (one per prototype condition), for example:

- `Virus Baseline_100_runs-spreadsheet.csv`
- `Virus No_infection_100_runs-spreadsheet.csv`
- `Virus Full_infection_100_runs-spreadsheet.csv`
- `Virus Low_spread_high_recovery_100_runs-spreadsheet.csv`
- `Virus High_spread_low_recovery_100_runs-spreadsheet.csv`

Skip this step if you only need Python-only plots (`--mode python`).

## 3. Run Python prototype experiments

Default: **100 runs × 52 ticks** per condition in `src/configs/prototype/`.

```bash
uv run python -m run.run_prototype
```

CSV output:

`results/data/python_prototype/`

## 4. Generate figures and comparison tables

```bash
uv run python -m run.plot_figures
```

## Final outputs

| Output | Location |
|--------|----------|
| Python experiment CSVs | `results/data/python_prototype/` |
| NetLogo reference CSVs | `results/data/netlogo_prototype/` |
| NetLogo trend plots | `results/analysis/replication/netlogo/*.png` |
| Python trend plots | `results/analysis/replication/python/*.png` |
| Python vs NetLogo (4 panels) | `results/analysis/replication/comparison/*_replication_compare.png` |
| Summary tables | `results/analysis/replication/comparison/*_summary.md` |
| Extension per-level trends | `results/analysis/extension/{00,01,02,05,10,25}/trends.png` |
| Extension aggregate figures | `results/analysis/extension/extension/` |

Plot only one part if needed:

```bash
uv run python -m run.plot_figures --mode netlogo
uv run python -m run.plot_figures --mode python
uv run python -m run.plot_figures --mode compare
```

## End-to-end (copy-paste)

```bash
uv sync --extra analysis
uv run python -m run.run_prototype
uv run python -m run.plot_figures
```

After step 2 (NetLogo CSVs in place), step 4 also produces comparison plots and markdown summaries.

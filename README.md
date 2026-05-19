# Virus Model Simulation

Python replication of the [NetLogo Virus model](https://ccl.northwestern.edu/netlogo/models/Virus) (SWEN90004 Assignment 2).

Two experiment stages:

1. **Replication (prototype)** — match NetLogo under five parameter sets; compare Python vs NetLogo.
2. **Extension** — immune reinfection sweep (`00`, `01`, `02`, `05`, `10`, `25`); Python only.

See `docs/experimental_design.md` for aims, conditions, and outputs. See `docs/architecture.md` for code layout.

## Prerequisites

- [Python 3.14+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

Run all commands from the **project root**.

## 1. Install dependencies

```bash
uv sync --extra analysis
```

`analysis` extra installs matplotlib (needed for `plot_*` only). Running experiments (`run_*`) uses the stdlib only.

---

## Replication (prototype)

### 2. Add NetLogo reference data (optional)

Export BehaviorSpace spreadsheets from NetLogo into:

`results/data/netlogo_prototype/`

Expected filenames (one per condition):

- `Virus Baseline_100_runs-spreadsheet.csv`
- `Virus No_infection_100_runs-spreadsheet.csv`
- `Virus Full_infection_100_runs-spreadsheet.csv`
- `Virus Low_spread_high_recovery_100_runs-spreadsheet.csv`
- `Virus High_spread_low_recovery_100_runs-spreadsheet.csv`

Skip if you only need Python-only plots (`plot_figures --mode python`).

### 3. Run Python replication

Configs: `src/configs/prototype/` (default **100 runs × 52 ticks** per condition).

```bash
uv run python -m run.run_prototype
```

CSV output: `results/data/python_prototype/`

### 4. Plot replication

```bash
uv run python -m run.plot_figures
```

Partial modes:

```bash
uv run python -m run.plot_figures --mode netlogo
uv run python -m run.plot_figures --mode python
uv run python -m run.plot_figures --mode compare
```

| Output | Location |
|--------|----------|
| NetLogo trend plots | `results/analysis/replication/netlogo/*.png` |
| Python trend plots | `results/analysis/replication/python/*.png` |
| Python vs NetLogo (4 panels) | `results/analysis/replication/comparison/*_replication_compare.png` |
| Summary tables | `results/analysis/replication/comparison/*_summary.md` |

---

## Extension

### 5. Run extension experiments

Configs: `src/configs/extension/` — `00.json` … `25.json` (reinfection probability 0%, 1%, 2%, 5%, 10%, 25%; **25%** is an additional stress-test level).

Default: **100 runs × 52 ticks** per level.

```bash
uv run python -m run.run_extension
```

Output:

- CSVs: `results/data/python_extension/` (`Virus Extension {level}_100_runs-spreadsheet.csv`)
- Metrics: `results/data/python_extension/{level}_run_metrics.json` (reinfection counts per run)

Longer horizons (optional):

```bash
uv run python -m run.run_extension --ticks 156 --output-dir results/data/python_extension_156ticks
uv run python -m run.run_extension --ticks 260 --output-dir results/data/python_extension_260ticks
```

### 6. Plot extension

```bash
uv run python -m run.plot_extension
```

Use `--ticks 156` (or `260`) if you ran long-horizon data into `python_extension_{N}ticks/`.

Partial modes: `trends`, `compare`, `survival`, `summary`, or `all` (default).

| Output | Location |
|--------|----------|
| Per-level trend + cumulative reinfections | `results/analysis/extension/{00,01,02,05,10,25}/trends.png` |
| Multi-level comparison (4 panels) | `results/analysis/extension/extension/reinfection_levels_compare.png` |
| Panels by metric | `results/analysis/extension/extension/{sick,immune,healthy,total}_by_reinfection.png` |
| Survival curve | `results/analysis/extension/extension/infection_survival_curve.png` |
| Total reinfections vs probability | `results/analysis/extension/extension/total_reinfections_by_probability.png` |
| Tables | `results/analysis/extension/extension/persistence.md`, `secondary_metrics.md` |

---

## End-to-end (copy-paste)

**Replication only** (with NetLogo CSVs already in `results/data/netlogo_prototype/`):

```bash
uv sync --extra analysis
uv run python -m run.run_prototype
uv run python -m run.plot_figures
```

**Extension only:**

```bash
uv sync --extra analysis
uv run python -m run.run_extension
uv run python -m run.plot_extension
```

**Both:**

```bash
uv sync --extra analysis
uv run python -m run.run_prototype
uv run python -m run.plot_figures
uv run python -m run.run_extension
uv run python -m run.plot_extension
```

---

## Data layout (summary)

| Role | Path |
|------|------|
| NetLogo replication CSVs | `results/data/netlogo_prototype/` |
| Python replication CSVs | `results/data/python_prototype/` |
| Python extension CSVs + metrics | `results/data/python_extension/` |
| Replication analysis | `results/analysis/replication/` |
| Extension analysis | `results/analysis/extension/` |

CLI overrides: `--runs`, `--ticks`, `--seed`, `--config-dir`, `--output-dir` on `run_*`; `--data-dir`, `--analysis-dir`, `--mode` on `plot_*`.

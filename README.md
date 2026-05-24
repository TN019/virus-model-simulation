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

`analysis` extra installs matplotlib (needed for analysis and report plots only). Running experiments (`run_*`) uses the stdlib only.

---

## Replication (prototype)

### 2. Add NetLogo reference data (optional)

Export BehaviorSpace spreadsheets from NetLogo into:

`output/netlogo_prototype/`

Expected filenames (one per condition):

- `Virus Baseline_100_runs-spreadsheet.csv`
- `Virus No_infection_100_runs-spreadsheet.csv`
- `Virus Full_infection_100_runs-spreadsheet.csv`
- `Virus Low_spread_high_recovery_100_runs-spreadsheet.csv`
- `Virus High_spread_low_recovery_100_runs-spreadsheet.csv`

Skip if you only need Python-only plots (`analysis.replication --mode python`).

### 3. Run Python replication

Configs: `src/configs/prototype/` (default **100 runs × 52 ticks** per condition).

```bash
uv run python -m run.run_prototype
```

CSV output: `output/python_prototype/`

### 4. Plot replication

```bash
uv run python -m analysis.replication
```

Partial modes:

```bash
uv run python -m analysis.replication --mode netlogo
uv run python -m analysis.replication --mode python
uv run python -m analysis.replication --mode compare
```

| Output | Location |
|--------|----------|
| NetLogo trend plots | `analysis/results/replication/netlogo/*.png` |
| Python trend plots | `analysis/results/replication/python/*.png` |
| Python vs NetLogo (4 panels) | `analysis/results/replication/comparison/*_replication_compare.png` |
| Summary tables | `analysis/results/replication/comparison/*_summary.md` |

---

## Extension

### 5. Run extension experiments

Configs: `src/configs/extension/` — `00.json` … `25.json` (reinfection probability 0%, 1%, 2%, 5%, 10%, 25%; **25%** is an additional stress-test level).

Default: **100 runs × 52 ticks** per level.

```bash
uv run python -m run.run_extension
```

Output:

- CSVs: `output/python_extension/` (`Virus Extension {level}_100_runs-spreadsheet.csv`)
- Metrics: `output/python_extension/{level}_run_metrics.csv` (reinfection counts per run)

Longer horizons (optional):

```bash
uv run python -m run.run_extension --ticks 156 --output-dir output/python_extension_156ticks
uv run python -m run.run_extension --ticks 260 --output-dir output/python_extension_260ticks
```

### 6. Plot extension

```bash
uv run python -m analysis.extension
```

Long-horizon data (read from `output/python_extension_{N}ticks/`, write figures under `analysis/results/extension_{N}ticks/`):

```bash
uv run python -m analysis.extension --ticks 156
uv run python -m analysis.extension --ticks 260
```

`analysis.extension` uses `--data-dir` and `--analysis-dir` (not `--output-dir`; that flag is only on `run_extension`).

Partial modes: `trends`, `compare`, `survival`, `summary`, or `all` (default).

| Output | Location |
|--------|----------|
| Per-level trend + cumulative reinfections | `analysis/results/extension/{00,01,02,05,10,25}/trends.png` |
| Multi-level comparison (4 panels) | `analysis/results/extension/extension/reinfection_levels_compare.png` |
| Panels by metric | `analysis/results/extension/extension/{sick,immune,healthy,total}_by_reinfection.png` |
| Survival curve | `analysis/results/extension/extension/infection_survival_curve.png` |
| Total reinfections vs probability | `analysis/results/extension/extension/total_reinfections_by_probability.png` |
| Tables | `analysis/results/extension/extension/persistence.md`, `secondary_metrics.md` |

---

## End-to-end (copy-paste)

**Replication only** (with NetLogo CSVs already in `output/netlogo_prototype/`):

```bash
uv sync --extra analysis
uv run python -m run.run_prototype
uv run python -m analysis.replication
```

**Extension only:**

```bash
uv sync --extra analysis
uv run python -m run.run_extension
uv run python -m analysis.extension
```

**Both:**

```bash
uv sync --extra analysis
uv run python -m run.run_prototype
uv run python -m analysis.replication
uv run python -m run.run_extension
uv run python -m analysis.extension
```

---

## Data layout (summary)

See [`output/README.md`](output/README.md) and [`analysis/README.md`](analysis/README.md) for what each folder and file type means.

| Role | Path |
|------|------|
| NetLogo replication CSVs | `output/netlogo_prototype/` |
| Python replication CSVs | `output/python_prototype/` |
| Python extension CSVs + metrics | `output/python_extension/` |
| Replication analysis | `analysis/results/replication/` |
| Extension analysis | `analysis/results/extension/` |
| Report figures | `plots/output/` |

CLI overrides: `--runs`, `--ticks`, `--seed`, `--config-dir`, `--output-dir` on `run_*`; `--data-dir`, `--analysis-dir`, `--mode` on `analysis.*`.

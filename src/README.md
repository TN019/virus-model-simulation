# src — How to Run

This directory contains the model, experiment scripts, and configs. **Running experiments requires only the Python 3.14+ standard library**; no third-party packages such as matplotlib are needed.

## Before You Run

1. Use **Python 3.14 or newer** (`python --version`).
2. In the terminal, change into the **`src` directory** (where this README lives):

```bash
cd <path to src>
```

**You must run** all `python -m run.*` commands below **from the `src` directory** (your working directory is this README’s path).

## Basic Commands

**Replication (comparison with NetLogo, 5 conditions):**

```bash
python -m run.run_prototype
```

**Extension (immune reinfection, 6 levels, default 52 ticks):**

```bash
python -m run.run_extension
```

**Extension long horizons (156 / 260 ticks):**

```bash
python -m run.run_extension --ticks 156 --output-dir output/python_extension_156ticks
python -m run.run_extension --ticks 260 --output-dir output/python_extension_260ticks
```

## Run Flow and Output

### Input

Commands read JSON configs from `configs/` (replication: `configs/prototype/`; extension: `configs/extension/`) and start runs using those parameters. `--runs`, `--ticks`, and `--seed` on the command line **override** the same fields in the JSON; if omitted, values from the config files are used.

### What Happens When You Run

1. Each condition in the config directory is executed in order (replication: 5 conditions / extension: 6 levels).
2. Under each condition, `--runs` independent runs are performed; the random seed for run `i` is `base_seed + i` (`i` starts at 0).
3. Each run advances the model for `--ticks` steps and records population statistics at every tick.
4. After all runs for a condition finish, results are written to the directory given by `--output-dir` (created automatically if missing).
5. The terminal prints progress for each condition, e.g. `[00] run 3/100` and the final file path.

### Default Scale and Random Seed

| Parameter | Default in config files | CLI override |
|-----------|-------------------------|--------------|
| `--runs` | **100** (100 independent replicates per condition) | `--runs 10` |
| `--ticks` | **52** (52 weeks per run) | `--ticks 156` |
| `--seed` | **`base_seed: 0`** | `--seed 42` |

The actual seed for a single run is `base_seed + run_id` (by default: run 0→0, run 1→1, …, run 99→99). Changing `--seed` shifts the random sequence for all runs, which helps with reproduction or comparison.

### Output Directory

Paths are relative to the **current working directory** (when executing from `src`, relative to `src/`). If `--output-dir` is not set, the default paths in the table below apply. **For long horizons (156 / 260 ticks), specify a directory explicitly** so results are not mixed with the default 52-tick output.

| Command | Default `--output-dir` |
|---------|------------------------|
| `run.run_prototype` | `output/python_prototype/` |
| `run.run_extension` (52 ticks) | `output/python_extension/` |
| `run.run_extension --ticks 156` | No dedicated default; specify one, e.g. `output/python_extension_156ticks/` |
| `run.run_extension --ticks 260` | No dedicated default; specify one, e.g. `output/python_extension_260ticks/` |

Examples for specifying output:

```bash
# Write under output/ inside src
python -m run.run_extension --output-dir output/python_extension

# Write to output/ at the repo root (use .. when running from src)
python -m run.run_extension --output-dir <path you want>
```

### Generated Files

**Replication** (one CSV per condition):

- `Virus {Condition}_100_runs-spreadsheet.csv` — BehaviorSpace Spreadsheet v2 format (sick / immune / healthy / total per run and tick, etc.)

**Extension** (two CSVs per level):

- `Virus Extension {level}_100_runs-spreadsheet.csv` — same as above, main time series
- `{level}_run_metrics.csv` — reinfection metrics (immune reinfections per run + cumulative reinfection series per tick)

The `100` in filenames comes from `runs` in the config; if you change `--runs` to another value, export still writes the actual number of runs, but the `output_file` name in the config is not renamed automatically.

## Common Parameter Examples

```bash
# Quick test: 2 replicates, 5 weeks, fixed seed
python -m run.run_extension --runs 2 --ticks 5 --seed 0

# Specify output directory
python -m run.run_extension --output-dir output/python_extension

# Long horizon 156 / 260 ticks (must set both --ticks and --output-dir)
python -m run.run_extension --ticks 156 --output-dir output/python_extension_156ticks
python -m run.run_extension --ticks 260 --output-dir output/python_extension_260ticks
```

Replication supports the same flags: `--runs`, `--ticks`, `--seed`, `--output-dir`, `--config-dir`.

## Configuration

Experiment parameter JSON lives in:

- `configs/prototype/` — replication
- `configs/extension/` — extension (`00.json` … `25.json`)

Use `--config-dir` to override the default config directory.

## Do Not Run Like This

```bash
python run/run_extension.py          # raises No module named 'scripts'
python -m src/run/run_extension.py # wrong module name
```

Always run from the **`src` directory** with: `python -m run.run_extension`.

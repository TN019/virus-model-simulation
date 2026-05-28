# How to Run and Configure Experiments

This directory contains the Python implementation, experiment scripts, and JSON configuration files for running the virus model experiments.

The project uses only the Python standard library. No third-party packages such as `matplotlib` are required.

---

## 1. Requirements

Use Python 3.14 or newer.

Check your Python version with:

```bash
python --version
```

---

## 2. Where to Run Commands

All commands must be run from the **project root**: the directory that contains this README and the `run/`, `configs/`, and `model/` folders.

Change into that directory first:

```bash
cd /path/to/your/project
```

Then run commands using the `python -m` module format.

For example:
```bash
python -m run.run_extension
```

Do not run the scripts directly with `python run/run_extension.py`, because the project uses module imports that require `python -m`.

---

## 3. Basic Commands

### Run the replication experiment

The replication experiment compares the Python model with the NetLogo version using 5 experiment conditions.

```bash
python -m run.run_prototype
```

By default, this reads configuration files from:

```text
configs/prototype/
```

and writes results to:

```text
output/python_prototype/
```

---

### Run the extension experiment

The extension experiment runs the immune reinfection model using 6 reinfection levels.

```bash
python -m run.run_extension
```

By default, this reads configuration files from:

```text
configs/extension/
```

and writes results to:

```text
output/python_extension/
```

---

### Run long-horizon extension experiments

For 156 ticks:

```bash
python -m run.run_extension --ticks 156 --output-dir output/python_extension_156ticks
```

For 260 ticks:

```bash
python -m run.run_extension --ticks 260 --output-dir output/python_extension_260ticks
```

When running long-horizon experiments, always specify a separate `--output-dir` so that long-horizon results are not mixed with the default 52-tick results.

---

## 4. Command-Line Options

Both `run.run_prototype` and `run.run_extension` support the same command-line options:

| Option         | Meaning                                  | Example                          |
| -------------- | ---------------------------------------- | -------------------------------- |
| `--runs`       | Number of independent runs per condition | `--runs 10`                      |
| `--ticks`      | Number of ticks per run                  | `--ticks 156`                    |
| `--seed`       | Base random seed                         | `--seed 42`                      |
| `--output-dir` | Directory where output files are written | `--output-dir output/test_run`   |
| `--config-dir` | Directory containing JSON config files   | `--config-dir configs/extension` |

The options `--runs`, `--ticks`, and `--seed` override the corresponding values in the JSON config files. `--output-dir` and `--config-dir` choose where results are written and which config directory is loaded; they are not fields in the JSON files.

For example:

```bash
python -m run.run_extension --runs 10 --ticks 52 --seed 42
```

This runs the extension experiment using:

* 10 independent runs per condition
* 52 ticks per run
* base random seed 42

---

## 5. Configuration Files

Experiment settings are stored as JSON files inside the `configs/` directory.

The replication experiment uses:

```text
configs/prototype/
```

The extension experiment uses:

```text
configs/extension/
```

Each JSON file represents one experiment condition.

For example, the extension config directory contains files such as:

```text
configs/extension/00.json
configs/extension/01.json
configs/extension/02.json
configs/extension/05.json
configs/extension/10.json
configs/extension/25.json
```

These correspond to different immune reinfection levels.

---

## 6. How Config Values Are Used

When an experiment is run:

1. The script reads all JSON config files from the selected config directory.
2. Each config file is treated as one condition.
3. Conditions are executed in order.
4. For each condition, the model runs multiple independent replicates.
5. Results are written to the selected output directory.

The main configurable values include:

| Config field     | Meaning                                         |
| ---------------- | ----------------------------------------------- |
| `runs`           | Number of independent replicates                |
| `ticks`          | Number of simulation ticks                      |
| `base_seed`      | Starting random seed                            |
| `output_file`    | Name of the main output CSV file                |
| model parameters | Parameters used to initialise and run the model |

---

## 7. Command-Line Overrides

The following command-line arguments override the same values in the JSON config files:

```text
--runs
--ticks
--seed
```

For example:

```bash
python -m run.run_extension --runs 20 --ticks 156 --seed 100
```

This overrides the config files and uses:

```text
runs = 20
ticks = 156
base_seed = 100
```

If these command-line options are not provided, the values from the JSON config files are used.

---

## 8. Random Seeds

The base seed is controlled by the config file or by the `--seed` command-line option.

For each independent run, the actual seed is calculated as:

```text
actual_seed = base_seed + run_id
```

where `run_id` starts from 0.

For example, if:

```text
base_seed = 0
runs = 100
```

then the runs use seeds:

```text
0, 1, 2, ..., 99
```

If you run:

```bash
python -m run.run_extension --seed 42
```

then the runs use seeds:

```text
42, 43, 44, ...
```

This makes experiments reproducible while still allowing each replicate to use a different random seed.

---

## 9. Output Files

### Replication experiment

The replication experiment writes one CSV file per condition.

Example output file:

```text
Virus {Condition}_100_runs-spreadsheet.csv
```

The file uses a BehaviorSpace-style spreadsheet format and records population statistics for each run and tick.

---

### Extension experiment

The extension experiment writes two CSV files per reinfection level:

```text
Virus Extension {level}_100_runs-spreadsheet.csv
{level}_run_metrics.csv
```

The spreadsheet CSV contains the main time-series results.

The run metrics CSV contains reinfection-related metrics, including:

* immune reinfections per run
* cumulative reinfections per tick

Output CSV names come from each config file’s `output_file` field (for example, `_100_runs-` in the default names). Changing `--runs` on the command line does not rename those files automatically.

---
# Experimental Design

## 1. Aim

This project has two experiment stages:

1. **Replication** — run the same parameter settings in NetLogo and Python and compare whether aggregate behaviour matches.
2. **Extension** — add imperfect immunity (immune reinfection) in Python only and study its effect on virus persistence.

Replication is **not** judged by tick-by-tick numerical equality. The Virus model is stochastic; NetLogo and Python may differ in RNG and update details. Success means similar **direction of change**, **trends**, and **summary statistics** under the same conditions.

---

## 2. Replication experiment

### 2.1 Aim

Determine whether the Python implementation reproduces the major behavioural patterns of the NetLogo Virus model under matched parameter settings.

### 2.2 Design

- **Conditions:** five shared parameter sets (see §2.3).
- **Runs per condition:** 100 (overridable in JSON or via `--runs`).
- **Horizon:** 52 ticks per run (one model year; overridable via `--ticks`).
- **Platforms:** each condition in NetLogo (BehaviorSpace) and Python (`uv run python -m run.run_prototype`).
- **Randomness:** `seed = base_seed + run_id` (default `base_seed: 0`); comparison uses means and distributions across runs.

### 2.3 Replication parameter sets

Shared parameters: `number_people = 150`, `initial_infected = 10`, `duration = 20`, `world_size = 35` (patches −17…17), `immunity_duration = 52`, `immune_reinfection_probability = 0`.

Config files: `src/configs/prototype/`

| Condition | Config file | Infectiousness | Chance recover | Purpose |
|-----------|-------------|---------------:|---------------:|---------|
| Baseline | `baseline.json` | 65 | 75 | Default NetLogo-matched behaviour |
| No infection | `no_infection.json` | 0 | 75 | Transmission shut off |
| Full infection | `full_infection.json` | 100 | 75 | Maximum transmission |
| Low spread, high recovery | `low_spread_high_recovery.json` | 20 | 90 | Weak spread, strong recovery |
| High spread, low recovery | `high_spread_low_recovery.json` | 90 | 20 | Strong spread, weak recovery |

These five conditions vary transmission and recovery only (fixed duration and immunity), so effects can be compared in isolation.

### 2.4 Outputs recorded (replication)

**Per tick** (each run), aligned with NetLogo reporters:

| Output | Meaning |
|--------|---------|
| Susceptible (“healthy”) | Not sick and not immune |
| Infected (“sick”) | Currently infectious |
| Immune | Temporarily immune |
| Total | Population size |
| % infected | Infected / total × 100 |
| % immune | Immune / total × 100 |

**Per run** (for comparison tables):

| Measure | Definition |
|---------|------------|
| Peak sick | Maximum infected count over the run |
| Peak week | Tick at which peak sick occurs |
| Final sick / immune / healthy / total | Values at the last tick |

**Across runs:** mean ± standard deviation; written to `results/analysis/replication/comparison/*_summary.md`.

### 2.5 Replication comparison method

Comparison does **not** require identical values at every tick.

**Visual**

- Single-source trends: `results/analysis/replication/netlogo/*.png`, `results/analysis/replication/python/*.png`.
- Overlay: `results/analysis/replication/comparison/*_replication_compare.png` — four panels (sick, immune, healthy, total), NetLogo mean vs Python mean.

**Tabular**

- `results/analysis/replication/comparison/*_summary.md` — peak and final metrics, NetLogo mean ± SD, Python mean ± SD, difference (Python − NetLogo).

**Judgement questions**

- Does the **baseline** condition show a similar outbreak shape?
- Does zero infectiousness suppress spread in both models?
- Does higher infectiousness increase infection in both models?
- Does lower recovery (high spread / low recovery) increase harm vs high recovery?
- Do summary statistics (peak sick, final immune, final total) point in the same direction?

### 2.6 Data and commands (replication)

| Role | Path |
|------|------|
| NetLogo BehaviorSpace CSVs | `results/data/netlogo_prototype/` |
| Python replication CSVs | `results/data/python_prototype/` |
| Analysis output | `results/analysis/replication/` |

```bash
uv run python -m run.run_prototype          # generate Python CSVs
uv run python -m run.plot_figures            # all modes: netlogo, python, compare
uv run python -m run.plot_figures --mode compare
```

NetLogo export filenames must match config `output_file` values (e.g. `Virus Baseline_100_runs-spreadsheet.csv`).

---

## 3. Extension experiment

### 3.1 Aim

Investigate how **imperfect immunity**, implemented as immune reinfection, affects reinfection events and population infection levels over time.

With `immune_reinfection_probability = 0`, recovered individuals become immune and cannot be reinfected until immunity expires (`PrototypeInfectionPolicy`). The extension allows immune individuals to become sick again with a configured probability when sharing a patch with an infectious carrier (`ExtensionInfectionPolicy`).

### 3.2 Research question

To what extent does imperfect immunity, implemented as immune reinfection, increase reinfection events and shift the population toward higher infection levels over time?

### 3.3 Design

- **New variable:** `immune_reinfection_probability` (0–100 scale, same convention as `infectiousness`).
- **Shared parameters:** same as replication except reinfection probability (see JSON in `src/configs/extension/`).
- **Six levels** (0–10% primary sweep; 25% optional stress-test):

| Config | `name` | Reinfection % | Purpose |
|--------|--------|-------------:|---------|
| `00.json` | `00` | 0 | Extension control (no immune reinfection) |
| `01.json` | `01` | 1 | Very low |
| `02.json` | `02` | 2 | Low |
| `05.json` | `05` | 5 | Medium |
| `10.json` | `10` | 10 | High |
| `25.json` | `25` | 25 | Additional stress-test (beyond primary sweep) |

- **Runs / ticks:** default 100 × 52 (overridable).
- **Platform:** Python only (reinfection is not in NetLogo).
- **Seeds:** `base_seed + run_id`, same as replication.

Immunity expiry is unchanged: immune agents may return to susceptible after `immunity_duration`, or become infectious early via reinfection.

### 3.4 Expected behaviour

Higher reinfection probability should:

- Increase **immune reinfection events** (counted per run in metrics JSON).
- Shift tick series toward **higher infected counts** (peak and trajectory).
- Increase spread opportunities when few susceptibles remain; persistence may rise as a consequence.

Effects may be non-linear (e.g. very high reinfection increasing turnover without monotonic persistence).

### 3.5 Extension outputs

**Per run (CSV):** same tick series as replication (BehaviorSpace Spreadsheet v2).

**Per condition (sidecar JSON):** `{name}_run_metrics.json` in the data directory, including:

- `immune_reinfections_per_run`
- `cumulative_reinfections_by_run`

**Data locations**

| Role | Path |
|------|------|
| Extension CSVs + metrics | `results/data/python_extension/` |
| Long horizon (optional) | `results/data/python_extension_{N}ticks/` (e.g. 156, 260) |

**Analysis output** (`uv run python -m run.plot_extension`):

| Output | Path |
|--------|------|
| Per-level trend + cumulative reinfections | `results/analysis/extension/{00,01,02,05,10,25}/trends.png` |
| Multi-level comparison (4 panels) | `results/analysis/extension/extension/reinfection_levels_compare.png` |
| Panels by metric | `results/analysis/extension/extension/{sick,immune,healthy,total}_by_reinfection.png` |
| Survival curve | `results/analysis/extension/extension/infection_survival_curve.png` |
| Total reinfections vs probability | `results/analysis/extension/extension/total_reinfections_by_probability.png` |
| Persistence table | `results/analysis/extension/extension/persistence.md` |
| Secondary metrics | `results/analysis/extension/extension/secondary_metrics.md` |

For `--ticks 156` or `260`, analysis writes under `results/analysis/extension_{N}ticks/` with the same internal layout (`00/` … `25/`, `extension/`).

```bash
uv run python -m run.run_extension
uv run python -m run.run_extension --ticks 156 --output-dir results/data/python_extension_156ticks
uv run python -m run.plot_extension --ticks 156
```

### 3.6 Hypothesis

Increasing immune reinfection probability **increases reinfection events** and **shifts the population toward higher infection levels over time**; at high levels this may also raise persistence, because immune individuals are no longer fully removed from the infectious chain.

---

## 4. Implementation notes

- **Terminology:** NetLogo “sick” = Python `infected`; “healthy” (not sick, not immune) = `susceptible`.
- **Export format:** BehaviorSpace Spreadsheet v2 CSV for direct comparison with NetLogo.
- **Replication scale:** 100 runs × 52 ticks per condition (`--runs` / `--ticks` on CLI).
- **Extension CSV names:** `Virus Extension {level}_100_runs-spreadsheet.csv` (e.g. `Virus Extension 10_100_runs-spreadsheet.csv`).

See `docs/architecture.md` for module layout and `README.md` for setup and end-to-end commands.

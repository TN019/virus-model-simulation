# Experimental Design

## 1. Aim

This project has two experiment stages:

1. **Replication** — run the same parameter settings in NetLogo and Python and compare whether aggregate behaviour matches.
2. **Extension** — add imperfect immunity (immune reinfection) in Python only and study its effect on virus persistence.

Replication is **not** judged by tick-by-tick numerical equality. The Virus model is stochastic; NetLogo and Python may differ in RNG and update details. Success means similar **direction of change**, **trends**, and **summary statistics** under the same conditions.

## 2. Replication experiment

### 2.1 Aim

Determine whether the Python implementation reproduces the major behavioural patterns of the NetLogo Virus model under matched parameter settings.

### 2.2 Design

- **Conditions:** five shared parameter sets (see §2.3).
- **Runs per condition:** 100 (configurable in JSON or via `--runs`).
- **Horizon:** 52 ticks per run (one model year; configurable via `--ticks`).
- **Platforms:** each condition run in NetLogo (BehaviorSpace) and Python (`scripts/run_baseline.py`).
- **Randomness:** different seeds per run; comparison uses means and distributions across runs.

### 2.3 Replication parameter sets

All conditions share: `number_people = 150`, `initial_infected = 10`, `duration = 20`, `world_size = 35` (patches −17…17), `immunity_duration = 52`, `immune_reinfection_probability = 0`. Config files live in `configs/baseline/`.

| Condition | Config file | Infectiousness | Chance recover | Purpose |
|-----------|-------------|---------------:|---------------:|---------|
| Baseline | `baseline.json` | 65 | 75 | Default NetLogo-matched behaviour |
| No infection | `no_infection.json` | 0 | 75 | Transmission shut off |
| Full infection | `full_infection.json` | 100 | 75 | Maximum transmission |
| Low spread, high recovery | `low_spread_high_recovery.json` | 20 | 90 | Weak spread, strong recovery |
| High spread, low recovery | `high_spread_low_recovery.json` | 90 | 20 | Strong spread, weak recovery |

These five conditions probe transmission strength and recovery rate without changing infection duration or immunity duration, so mechanisms can be compared in isolation.

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

**Across runs:** mean ± standard deviation of the above per-run measures; used in `results/analysis/replication_experiment/*_summary.md`.

### 2.5 Replication comparison method

Comparison does **not** require identical values at every tick.

**Visual comparison**

- Single-source trends: `results/analysis/netlogo_baseline/*.png`, `results/analysis/python_baseline/*.png` (sick, immune, healthy, total vs week).
- Overlay: `results/analysis/replication_experiment/*_replication_compare.png` — four panels (sick, immune, healthy, total), NetLogo mean vs Python mean.

**Tabular comparison**

- `results/analysis/replication_experiment/*_summary.md` — peak and final metrics with NetLogo mean ± SD, Python mean ± SD, and difference (Python − NetLogo).

**Judgement questions**

- Does the baseline condition show a similar outbreak shape?
- Does zero infectiousness suppress spread in both models?
- Does higher infectiousness increase infection in both models?
- Does lower recovery (high spread / low recovery) increase harm vs high recovery?
- Do summary statistics (peak sick, final immune, final total) point in the same direction?

Python replication is successful if trends and summary directions agree; large systematic offsets may remain due to implementation differences.

### 2.6 Data locations

| Role | Path |
|------|------|
| NetLogo BehaviorSpace CSVs | `results/data/netlogo_baseline/` |
| Python replication CSVs | `results/data/python_baseline/` |
| Analysis figures | `results/analysis/` |

Generate analysis after experiments: `uv run python scripts/plot_figures.py` (see `README.md`).

---

## 3. Extension experiment

### 3.1 Aim

Investigate how **imperfect immunity** affects long-term virus persistence and outbreak dynamics.

In the baseline model, recovered individuals become immune and cannot be reinfected until immunity expires. The extension allows immune individuals to become sick again with a small probability when sharing a patch with an infectious individual (`ExtensionInfectionPolicy`).

### 3.2 Research question

Does increasing the probability of reinfection among immune individuals increase the likelihood that the virus persists in the population?

### 3.3 Design

- **New variable:** `immune_reinfection_probability` (same 0–100 scale as `infectiousness` in code).
- **Baseline behaviour** (`immune_reinfection_probability = 0`) is covered by the replication experiment — not repeated as a separate extension condition.
- **Planned extension levels:**

| Condition | Reinfection probability | Purpose |
|-----------|------------------------:|---------|
| Low imperfect immunity | 2 (≈2% per contact) | Small chance of immune failure |
| Medium imperfect immunity | 5 (≈5%) | Moderate effect |
| High imperfect immunity | 10 (≈10%) | Stronger imperfect immunity |

Config JSON files belong in `configs/extension/` (same shared parameters as baseline except reinfection probability). Run with `scripts/run_extension.py`; output to `results/data/python_extension/`.

- **Runs / ticks:** same defaults as replication (100 × 52 unless overridden).
- **NetLogo:** not used — reinfection is new Python-only behaviour.

Immunity expiry is unchanged: immune individuals may still return to susceptible when `immunity_duration` ends, or become infectious early via reinfection.

### 3.4 Expected behaviour

Higher reinfection probability should:

- Increase opportunities for spread when few susceptibles remain.
- Raise persistence and/or final infected levels.
- Possibly affect population size through compounded outbreaks.

Effects may be non-linear (e.g. very high reinfection increasing turnover without monotonic persistence).

### 3.5 Extension outputs

Same per-tick series as replication. Primary summary interest:

- Persistence at final tick (infected > 0)
- Peak and final infected percentage
- Time to extinction (if infected reaches zero)
- Final population size
- Distribution of outcomes across runs (not only the mean curve)

Extension-specific analysis plots can mirror the baseline pipeline once `configs/extension/` and `results/data/python_extension/` are populated.

### 3.6 Hypothesis

Increasing immune reinfection probability **increases virus persistence** and delays or prevents extinction, because immune individuals are no longer fully removed from the infectious chain.

---

## 4. Implementation notes

- **Terminology:** NetLogo “sick” = Python `infected`; “healthy” (not sick, not immune) = `susceptible`.
- **Export format:** Python writes BehaviorSpace Spreadsheet v2 CSV for direct comparison with NetLogo exports.
- **Quick tests:** `--runs 2 --ticks 10` for fast smoke runs; full replication uses 100 × 52.

See `docs/architecture.md` for module layout and `README.md` for commands to reproduce final results.

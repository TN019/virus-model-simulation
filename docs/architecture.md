# Architecture

```
src/
├── model/              # Core ABM: Person, World, VirusSimulation, infection policies
├── configs/
│   ├── prototype/      # Five replication conditions (JSON)
│   └── extension/      # Six reinfection levels: 00, 01, 02, 05, 10, 25 (JSON)
├── scripts/            # Experiment execution (no plotting)
│   ├── common/         # Condition loading, BehaviorSpace CSV export, console output
│   ├── prototype/      # Replication experiment runner
│   └── extension/      # Extension runner (+ per-run metrics JSON)
├── run/                # Thin CLI entry points (delegate to scripts/ or analysis/)
└── analysis/           # Read CSVs / metrics; write figures and markdown tables
    ├── common/         # Spreadsheet parsing, shared plot helpers, output path helpers
    ├── replication/    # NetLogo vs Python replication plots and summaries
    └── extension/      # Extension trends, comparisons, persistence tables
```

### `model/`

- **`VirusSimulation`** — tick loop: movement, infection, recovery, immunity expiry, reproduction, statistics.
- **`PrototypeInfectionPolicy`** — NetLogo-aligned transmission (susceptible only).
- **`ExtensionInfectionPolicy`** — adds immune reinfection when `immune_reinfection_probability > 0`.
- Policy is chosen automatically from config (`ExtensionInfectionPolicy` if probability > 0, else `PrototypeInfectionPolicy`).

### `scripts/`

Loads JSON from `src/configs/`, runs stochastic replicates, writes **BehaviorSpace Spreadsheet v2** CSVs under `results/data/`. Extension runs also write `{condition}_run_metrics.json` (reinfection counts and cumulative series per run).

Uses **stdlib only** (no matplotlib).

### `analysis/`

Reads experiment output and writes PNG figures and markdown summaries under `results/analysis/`. Requires the optional `analysis` dependency (`matplotlib`).

### `run/`

Entry modules invoked as `python -m run.<module>` (typically via `uv run`):

| Module | Delegates to | Output |
|--------|----------------|--------|
| `run_prototype` | `scripts.prototype` | Replication CSVs |
| `run_extension` | `scripts.extension` | Extension CSVs + metrics JSON |
| `plot_figures` | `analysis.replication` | Replication figures |
| `plot_extension` | `analysis.extension` | Extension figures |

## Repository layout

```
virus-model-simulation/
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
│
├── src/                    # (see code layers above)
│
├── results/
│   ├── data/               # Raw experiment output (CSV + extension metrics)
│   │   ├── netlogo_prototype/
│   │   ├── python_prototype/
│   │   ├── python_extension/
│   │   └── python_extension_{N}ticks/   # optional long horizons (e.g. 156, 260)
│   └── analysis/           # Generated figures and tables
│       ├── replication/
│       │   ├── netlogo/        # Per-condition trends (NetLogo)
│       │   ├── python/         # Per-condition trends (Python)
│       │   └── comparison/     # 4-panel overlays + *_summary.md
│       └── extension/
│           ├── 00/ … 25/       # Per-level trends (trends.png)
│           └── extension/      # Cross-level figures and *.md tables
│
└── docs/
    ├── architecture.md
    ├── experimental_design.md
    ├── domain_model.png / .drawio
    ├── state_machine_baseline.png / .drawio
    ├── state_machine_extension.png / .drawio
    ├── fsp_person_lifecycle_baseline.png / .lts
    └── fsp_person_lifecycle_extension.png / .lts
```

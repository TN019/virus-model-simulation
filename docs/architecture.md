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
└── run/                # Thin CLI entry points (delegate to scripts/)
```

```
analysis/               # Read CSVs / metrics; write figures and markdown tables
├── common/             # Spreadsheet parsing, shared plot helpers, output path helpers
├── replication/        # NetLogo vs Python replication plots and summaries
├── extension/          # Extension trends, comparisons, persistence tables
└── results/            # Generated figures and tables (not Python package code)
```

```
plots/                  # Report-ready summary figures (reads output/ + analysis/results/)
├── plot_report_figures.py
└── output/
```

### `model/`

- **`VirusSimulation`** — tick loop: movement, infection, recovery, immunity expiry, reproduction, statistics.
- **`PrototypeInfectionPolicy`** — NetLogo-aligned transmission (susceptible only).
- **`ExtensionInfectionPolicy`** — adds immune reinfection when `immune_reinfection_probability > 0`.
- Policy is chosen automatically from config (`ExtensionInfectionPolicy` if probability > 0, else `PrototypeInfectionPolicy`).

### `scripts/`

Loads JSON from `src/configs/`, runs stochastic replicates, writes **BehaviorSpace Spreadsheet v2** CSVs under `output/`. Extension runs also write `{condition}_run_metrics.csv` (reinfection counts and cumulative series per run).

Uses **stdlib only** (no matplotlib).

### `analysis/`

Reads experiment output from `output/` and writes PNG figures and markdown summaries under `analysis/results/`. Requires the optional `analysis` dependency (`matplotlib`).

### `run/`

Entry modules invoked as `python -m run.<module>` (typically via `uv run`):

| Module | Delegates to | Output |
|--------|----------------|--------|
| `run_prototype` | `scripts.prototype` | Replication CSVs |
| `run_extension` | `scripts.extension` | Extension CSVs + metrics JSON |

Analysis entry points: `python -m analysis.replication`, `python -m analysis.extension`.

### `plots/`

Standalone report figures that combine raw data and analysis summaries. Output goes to `plots/output/`.

## Repository layout

```
virus-model-simulation/
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
│
├── src/                    # Model + experiment runners (see above)
│
├── output/                 # Raw experiment output (CSV + extension metrics)
│   ├── netlogo_prototype/
│   ├── python_prototype/
│   ├── python_extension/
│   └── python_extension_{N}ticks/   # optional long horizons (e.g. 156, 260)
│
├── analysis/               # Analysis code + generated figures/tables
│   ├── common/
│   ├── replication/
│   ├── extension/
│   └── results/
│       ├── replication/
│       │   ├── netlogo/        # Per-condition trends (NetLogo)
│       │   ├── python/         # Per-condition trends (Python)
│       │   └── comparison/     # 4-panel overlays + *_summary.md
│       └── extension/
│           ├── 00/ … 25/       # Per-level trends (trends.png)
│           └── extension/      # Cross-level figures and *.md tables
│
├── plots/                  # Report figures
│   └── output/
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

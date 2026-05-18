# Architecture

Python replication of the NetLogo Virus model for SWEN90004 Assignment 2. The codebase separates the agent-based model, experiment execution, and post-run analysis.

## Repository layout

```
virus-model-simulation/
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
│
├── configs/
│   ├── baseline/              # 5 replication conditions (JSON)
│   └── extension/             # extension conditions (JSON, when added)
│
├── src/
│   ├── virus_model/           # core simulation
│   ├── run/                   # experiment runners + BehaviorSpace export
│   └── analysis/              # CSV parsing, plots, summary tables
│
├── scripts/
│   ├── run_baseline.py        # run.baseline.main()
│   ├── run_extension.py       # run.extension.main()
│   └── plot_figures.py        # analysis.cli.main()
│
├── results/
│   ├── data/
│   │   ├── netlogo_baseline/  # NetLogo BehaviorSpace CSVs (reference)
│   │   ├── python_baseline/   # Python replication CSVs
│   │   └── python_extension/  # Python extension CSVs
│   └── analysis/
│       ├── netlogo_baseline/  # per-condition trend plots (NetLogo)
│       ├── python_baseline/   # per-condition trend plots (Python)
│       └── compare/           # 4-panel overlays + summary markdown
│
├── tests/
└── docs/
    ├── cx_asg_2_2026.pdf
    ├── architecture.md
    ├── domain_model.png
    ├── domain_model.drawio
    ├── state_machine_baseline.png
    ├── state_machine_baseline.drawio
    ├── state_machine_extension.png
    ├── state_machine_extension.drawio
    ├── fsp_person_lifecycle_baseline.png
    ├── fsp_person_lifecycle_baseline.lts
    ├── fsp_person_lifecycle_extension.png
    ├── fsp_person_lifecycle_extension.lts
    └── experimental_design.md
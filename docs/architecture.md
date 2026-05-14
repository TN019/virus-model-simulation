virus-project/
├── README.md
├── pyproject.toml          
├── uv.lock                 
├── .python-version
├── .gitignore
│
├── configs/
│   ├── baseline.json
│   ├── infectiousness_low.json
│   ├── infectiousness_high.json
│   ├── recovery_low.json
│   ├── extension_immunity_02.json
│   ├── extension_immunity_05.json
│   └── extension_immunity_10.json
│
├── src/
│   └── virus_model/
│       ├── config.py
│       ├── state.py
│       ├── person.py
│       ├── world.py
│       ├── policies.py
│       ├── simulation.py
│       ├── stats.py
│       └── experiment_runner.py
│
├── scripts/
│   ├── run_baseline.py
│   ├── run_experiments.py
│   ├── run_extension.py
│   └── generate_plots.py
│
├── analysis/
│   ├── analyse_baseline.py
│   ├── compare_conditions.py
│   ├── compare_netlogo_python.py
│   └── plot_results.py
│
├── outputs/
│   ├── raw/
│   ├── summaries/
│   ├── figures/
│   └── logs/
│
├── tests/
│   ├── test_person_state.py
│   ├── test_world.py
│   ├── test_infection.py
│   ├── test_recovery_death.py
│   ├── test_reproduction.py
│   └── test_simulation_step.py
│
└── docs/
    ├── cx_asg_2_2026.pdf
    ├── architecture.md
    ├── domain_mode.png
    ├── domain_mode.drawio
    ├── state_machine_baseline.png
    ├── state_machine_baseline.drawio
    ├── state_machine_extension.png
    ├── state_machine_extension.drawio
    ├── fsp_person_lifecycle_baseline.png
    ├── fsp_person_lifecycle_baseline.lts
    ├── fsp_person_lifecycle_extension.png
    ├── fsp_person_lifecycle_extension.lts
    └── experimental_design.md
# Output 目录说明

本目录存放实验的**原始数据**（CSV 与 extension 指标 JSON）。除 NetLogo 导出的 CSV 需手动放入外，其余均可通过 `uv run python -m run.*` 重新生成。

---

## 总览

```
output/
├── netlogo_prototype/          # NetLogo 参考数据（手动放入）
├── python_prototype/           # Python replication CSV
├── python_extension/           # Python extension CSV + metrics JSON
└── python_extension_{N}ticks/  # 长周期 extension 数据（可选）
```

| 阶段 | 生成命令 | 原始数据 |
|------|----------|----------|
| Replication（与 NetLogo 对照） | `run.run_prototype` | `python_prototype/` |
| Extension（免疫再感染） | `run.run_extension` | `python_extension/` |

---

## `netlogo_prototype/`

- **含义：** NetLogo BehaviorSpace 导出的参考数据（**手动**从 NetLogo 放入）。
- **用途：** 与 Python replication 结果对比；`analysis.replication --mode compare` 需要此目录。
- **文件示例：** `Virus Baseline_100_runs-spreadsheet.csv` 等 5 个条件（与 `src/configs/prototype/` 中 `output_file` 一致）。

## `python_prototype/`

- **含义：** Python **replication** 实验的 BehaviorSpace 格式 CSV。
- **生成：** `uv run python -m run.run_prototype`
- **配置：** `src/configs/prototype/`（baseline、no_infection、full_infection 等 5 条件）
- **默认规模：** 100 runs × 52 ticks/条件

## `python_extension/`

- **含义：** Python **extension** 实验 CSV + 每条条件的指标 JSON。
- **生成：** `uv run python -m run.run_extension`
- **配置：** `src/configs/extension/`（`00.json` … `25.json`，再感染概率 0%–25%）
- **CSV 示例：** `Virus Extension 10_100_runs-spreadsheet.csv`
- **指标 JSON：** `10_run_metrics.json`（含 `immune_reinfections_per_run`、`cumulative_reinfections_by_run` 等）

## `python_extension_{N}ticks/`

- **含义：** 与 `python_extension/` 相同，但仿真长度为 **N 周**（如 156、260）。
- **生成：**  
  `uv run python -m run.run_extension --ticks N --output-dir output/python_extension_{N}ticks`

---

## 命名说明

- **`prototype`：** 指 replication 实验（与 NetLogo 对照），不是某个单独条件名。
- **`baseline`：** replication 中的默认条件（`baseline.json`），输出 `Virus Baseline_100_runs-spreadsheet.csv`。
- **BehaviorSpace CSV：** 与 NetLogo 导出格式对齐，便于逐 run、逐 tick 对比。

---

## 如何重新生成

保留 `netlogo_prototype/` 时，可删除其余 `output/` 子目录，然后：

```bash
uv run python -m run.run_prototype
uv run python -m run.run_extension
```

长周期需分别跑 `run_extension` 并带上对应的 `--ticks` 与 `--output-dir`。

分析图表见 [`analysis/README.md`](../analysis/README.md)。更完整的实验设计与命令见根目录 `README.md` 与 `docs/experimental_design.md`。

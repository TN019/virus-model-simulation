# Results 目录说明

本目录存放实验的**原始数据**（`data/`）和**分析输出**（`analysis/`）。除 NetLogo 导出的 CSV 需手动放入外，其余均可通过项目根目录下的 `uv run python -m run.*` / `plot_*` 重新生成。

---

## 总览

```
results/
├── data/          # 实验跑出来的 CSV 与 extension 指标 JSON（输入给 analysis）
└── analysis/      # 根据 data 生成的图与 Markdown 表（matplotlib）
```

| 阶段 | 生成命令 | 原始数据 | 分析结果 |
|------|----------|----------|----------|
| Replication（与 NetLogo 对照） | `run.run_prototype` → `plot_figures` | `data/python_prototype/` | `analysis/replication/` |
| Extension（免疫再感染） | `run.run_extension` → `plot_extension` | `data/python_extension/` | `analysis/extension/` |

---

## `data/` — 原始实验输出

### `data/netlogo_prototype/`

- **含义：** NetLogo BehaviorSpace 导出的参考数据（**手动**从 NetLogo 放入）。
- **用途：** 与 Python replication 结果对比；`plot_figures --mode compare` 需要此目录。
- **文件示例：** `Virus Baseline_100_runs-spreadsheet.csv` 等 5 个条件（与 `src/configs/prototype/` 中 `output_file` 一致）。

### `data/python_prototype/`

- **含义：** Python **replication** 实验的 BehaviorSpace 格式 CSV。
- **生成：** `uv run python -m run.run_prototype`
- **配置：** `src/configs/prototype/`（baseline、no_infection、full_infection 等 5 条件）
- **默认规模：** 100 runs × 52 ticks/条件

### `data/python_extension/`

- **含义：** Python **extension** 实验 CSV + 每条条件的指标 JSON。
- **生成：** `uv run python -m run.run_extension`
- **配置：** `src/configs/extension/`（`00.json` … `25.json`，再感染概率 0%–25%）
- **CSV 示例：** `Virus Extension 10_100_runs-spreadsheet.csv`
- **指标 JSON：** `10_run_metrics.json`（含 `immune_reinfections_per_run`、`cumulative_reinfections_by_run` 等）

### `data/python_extension_{N}ticks/`

- **含义：** 与 `python_extension/` 相同，但仿真长度为 **N 周**（如 156、260）。
- **生成：**  
  `uv run python -m run.run_extension --ticks N --output-dir results/data/python_extension_{N}ticks`

---

## `analysis/` — 图表与汇总（由 data 生成）

分析脚本**只读** `data/`，**写入** `analysis/`。需已安装 `uv sync --extra analysis`。

### `analysis/replication/`

Replication 实验的可视化与 Python vs NetLogo 对照。

| 子目录 | 含义 | 生成方式 |
|--------|------|----------|
| `netlogo/` | 各条件的 NetLogo 趋势图（sick / immune / healthy / total） | `plot_figures --mode netlogo` |
| `python/` | 各条件的 Python 趋势图 | `plot_figures --mode python` |
| `comparison/` | 四宫格叠加图 `*_replication_compare.png` 与 `*_summary.md` | `plot_figures --mode compare` |

- **输入数据：** `data/netlogo_prototype/` + `data/python_prototype/`
- **命令：** `uv run python -m run.plot_figures`

### `analysis/extension/`（默认 52 ticks）

Extension 实验的可视化（与 `data/python_extension/` 对应）。

| 子目录 / 文件 | 含义 |
|---------------|------|
| `00/` … `25/` | 每个再感染档位一张 `trends.png`（人口趋势 + 累计免疫再感染） |
| `extension/reinfection_levels_compare.png` | 六档对比四宫格 |
| `extension/{sick,immune,healthy,total}_by_reinfection.png` | 按指标分的多档曲线 |
| `extension/infection_survival_curve.png` | 感染存活曲线 |
| `extension/total_reinfections_by_probability.png` | 再感染概率 vs 总再感染次数 |
| `extension/persistence.md` | 持久性（末 tick 仍有感染者）汇总表 |
| `extension/secondary_metrics.md` | 灭绝时间、峰值感染等次级指标表 |

- **命令：** `uv run python -m run.plot_extension`

### `analysis/extension_{N}ticks/`

- **含义：** 与 `analysis/extension/` 结构相同，对应 `data/python_extension_{N}ticks/` 的长周期结果。
- **命令：** `uv run python -m run.plot_extension --ticks N`  
  （不要用 `--output-dir`；画图用 `--analysis-dir` 时默认仍会在 `results/analysis/` 下生成 `extension_{N}ticks/`）

---

## 档位编号（extension）

| 目录名 | 配置 | 免疫再感染概率 | 说明 |
|--------|------|----------------|------|
| `00` | `00.json` | 0% | Extension 对照 |
| `01` | `01.json` | 1% | 主 sweep |
| `02` | `02.json` | 2% | 主 sweep |
| `05` | `05.json` | 5% | 主 sweep |
| `10` | `10.json` | 10% | 主 sweep |
| `25` | `25.json` | 25% | 额外 stress-test |

---

## 命名说明

- **`prototype`：** 指 replication 实验（与 NetLogo 对照），不是某个单独条件名。
- **`baseline`：** replication 中的默认条件（`baseline.json`），输出 `Virus Baseline_100_runs-spreadsheet.csv`。
- **BehaviorSpace CSV：** 与 NetLogo 导出格式对齐，便于逐 run、逐 tick 对比。
- **`*_summary.md`：** 某条件下 Python 与 NetLogo 的 peak/final 指标均值 ± 标准差及差值。

---

## 如何重新生成

保留 `data/netlogo_prototype/` 时，可删除其余 `data/` 与整个 `analysis/`，然后：

```bash
uv run python -m run.run_prototype
uv run python -m run.plot_figures

uv run python -m run.run_extension
uv run python -m run.plot_extension
```

长周期需分别跑 `run_extension` / `plot_extension` 并带上对应的 `--ticks` 与（仅 run 时）`--output-dir`。

更完整的实验设计与命令见仓库根目录 `README.md` 与 `docs/experimental_design.md`。

# Analysis 目录说明

本目录包含**分析代码**（`common/`、`replication/`、`extension/`）和**分析输出**（`results/`）。分析脚本只读 `output/`，写入 `analysis/results/`。需已安装 `uv sync --extra analysis`。

---

## 总览

```
analysis/
├── common/         # spreadsheet 解析、共享 plot 工具、路径 helper
├── replication/    # replication 分析 CLI 与画图逻辑
├── extension/      # extension 分析 CLI 与画图逻辑
└── results/        # 生成的图与 Markdown 表（matplotlib）
```

| 阶段 | 生成命令 | 输入数据 | 分析结果 |
|------|----------|----------|----------|
| Replication | `analysis.replication` | `output/netlogo_prototype/` + `output/python_prototype/` | `results/replication/` |
| Extension | `analysis.extension` | `output/python_extension/` | `results/extension/` |

---

## `results/replication/`

Replication 实验的可视化与 Python vs NetLogo 对照。

| 子目录 | 含义 | 生成方式 |
|--------|------|----------|
| `netlogo/` | 各条件的 NetLogo 趋势图（sick / immune / healthy / total） | `analysis.replication --mode netlogo` |
| `python/` | 各条件的 Python 趋势图 | `analysis.replication --mode python` |
| `comparison/` | 四宫格叠加图 `*_replication_compare.png` 与 `*_summary.md` | `analysis.replication --mode compare` |

- **命令：** `uv run python -m analysis.replication`

## `results/extension/`（默认 52 ticks）

Extension 实验的可视化（与 `output/python_extension/` 对应）。

| 子目录 / 文件 | 含义 |
|---------------|------|
| `00/` … `25/` | 每个再感染档位一张 `trends.png`（人口趋势 + 累计免疫再感染） |
| `extension/reinfection_levels_compare.png` | 六档对比四宫格 |
| `extension/{sick,immune,healthy,total}_by_reinfection.png` | 按指标分的多档曲线 |
| `extension/infection_survival_curve.png` | 感染存活曲线 |
| `extension/total_reinfections_by_probability.png` | 再感染概率 vs 总再感染次数 |
| `extension/persistence.md` | 持久性（末 tick 仍有感染者）汇总表 |
| `extension/secondary_metrics.md` | 灭绝时间、峰值感染等次级指标表 |

- **命令：** `uv run python -m analysis.extension`

## `results/extension_{N}ticks/`

- **含义：** 与 `results/extension/` 结构相同，对应 `output/python_extension_{N}ticks/` 的长周期结果。
- **命令：** `uv run python -m analysis.extension --ticks N`  
  （不要用 `--output-dir`；画图用 `--analysis-dir` 时默认仍会在 `analysis/results/` 下生成 `extension_{N}ticks/`）

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

## 如何重新生成

保留 `output/netlogo_prototype/` 时，可删除 `results/` 下全部内容，然后：

```bash
uv run python -m analysis.replication
uv run python -m analysis.extension
```

长周期需分别跑 `analysis.extension` 并带上对应的 `--ticks`。

报告用汇总图见 `plots/plot_report_figures.py`（输出到 `plots/output/`）。更完整的实验设计与命令见根目录 `README.md` 与 `docs/experimental_design.md`。

from __future__ import annotations

import statistics
from dataclasses import dataclass

from analysis.common.spreadsheet import RunSummary, load_per_run_summaries


@dataclass(frozen=True)
class MetricComparison:
    name: str
    netlogo: str
    python: str
    difference: str


def _mean_sd(values: list[float], *, digits: int = 1) -> str:
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return f"{mean:.{digits}f} ± {sd:.{digits}f}"


def _difference(python_values: list[float], netlogo_values: list[float], *, digits: int = 1) -> str:
    delta = statistics.mean(python_values) - statistics.mean(netlogo_values)
    return f"{delta:+.{digits}f}"


def build_summary_rows(python_csv: str, netlogo_csv: str) -> list[MetricComparison]:
    python_runs = load_per_run_summaries(python_csv)
    netlogo_runs = load_per_run_summaries(netlogo_csv)

    def row(
        name: str,
        python_attr: str,
        netlogo_attr: str,
        *,
        digits: int = 1,
    ) -> MetricComparison:
        py_vals = [getattr(run, python_attr) for run in python_runs]
        nl_vals = [getattr(run, netlogo_attr) for run in netlogo_runs]
        return MetricComparison(
            name=name,
            netlogo=_mean_sd(nl_vals, digits=digits),
            python=_mean_sd(py_vals, digits=digits),
            difference=_difference(py_vals, nl_vals, digits=digits),
        )

    return [
        row("peak sick", "peak_sick", "peak_sick"),
        row("peak week", "peak_week", "peak_week", digits=0),
        row("final sick", "final_sick", "final_sick"),
        row("final immune", "final_immune", "final_immune"),
        row("final healthy", "final_healthy", "final_healthy"),
        row("final total", "final_total", "final_total"),
    ]


def render_summary_markdown(
    rows: list[MetricComparison],
    *,
    condition: str,
) -> str:
    lines = [
        f"# Replication summary — {condition}",
        "",
        "| Metric | NetLogo mean ± SD | Python mean ± SD | Difference |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(f"| {row.name} | {row.netlogo} | {row.python} | {row.difference} |")
    lines.append("")
    lines.append("_Difference = Python mean − NetLogo mean._")
    lines.append("")
    return "\n".join(lines)

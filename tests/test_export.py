import csv
from pathlib import Path

from run.export import write_behaviorspace_spreadsheet
from run.conditions import ConditionSpec
from virus_model.stats import TickRecord


def test_behaviorspace_export_has_expected_sections(tmp_path: Path) -> None:
    spec = ConditionSpec("baseline", "test.csv", 65, 75)
    config = spec.to_config(runs=2, ticks=2)
    runs = [
        [
            TickRecord(0, 140, 10, 0, 150, 6.666666666666667, 0.0),
            TickRecord(1, 138, 12, 0, 150, 8.0, 0.0),
            TickRecord(2, 136, 14, 0, 150, 9.333333333333334, 0.0),
        ],
        [
            TickRecord(0, 140, 10, 0, 150, 6.666666666666667, 0.0),
            TickRecord(1, 139, 11, 0, 150, 7.333333333333333, 0.0),
            TickRecord(2, 137, 13, 0, 150, 8.666666666666666, 0.0),
        ],
    ]
    path = tmp_path / "test.csv"
    write_behaviorspace_spreadsheet(
        path,
        experiment_name="baseline_2_runs",
        config=config,
        all_runs=runs,
    )
    rows = list(csv.reader(path.open()))
    labels = [row[0] for row in rows if row]
    assert "[reporter]" in labels
    assert "[all run data]" in labels
    assert "[final]" in labels

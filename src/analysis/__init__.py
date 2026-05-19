"""Load experiment spreadsheets and generate analysis figures."""

from analysis.extension.cli import main as plot_extension_main
from analysis.replication.cli import main as plot_replication_main

__all__ = ["plot_replication_main", "plot_extension_main"]

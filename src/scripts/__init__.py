"""Experiment runners and NetLogo-aligned export."""
from scripts.prototype.cli import main as run_prototype_main
from scripts.extension.cli import main as run_extension_main

__all__ = ["run_prototype_main", "run_extension_main"]

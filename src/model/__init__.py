"""Public model API: configuration and simulation entry point."""
from model.config import SimulationConfig
from model.simulation import VirusSimulation

__all__ = ["SimulationConfig", "VirusSimulation"]

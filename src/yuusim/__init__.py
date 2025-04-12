"""
Main Module of yuusim

This module acts as the entry - point for the `yuusim` package. It provides a unified interface
to access core functionalities and utility components of the simulation system.

Functions, Classes, and Sub - modules
--------------------------------------
- `SimulationEnvironment`: The main class responsible for managing the simulation environment,
  including project initialization, configuration loading, and simulation execution.
- `io`: A sub - module that contains functions related to input and output operations, such as
  loading configuration files and saving simulation results.
- `utils`: A sub - module that provides various utility functions, including exception handling,
  performance optimization, and type definitions.

Examples
--------
>>> from yuusim import SimulationEnvironment
>>> env = SimulationEnvironment("my_project")

"""

from . import io, utils
from .simulation import SimulationEnvironment

__all__ = ["SimulationEnvironment", "io", "utils"]

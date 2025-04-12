"""
`__init__.py` Module Documentation
==================================

This module serves as the entry point for the `yuusim.io` package. It aggregates and exports key functions
related to configuration management, data I/O operations, and logging setup, providing a convenient
interface for users to interact with these functionalities.

Exported Functions
------------------
- `load_config`: Load configuration data from a file.
- `save_config`: Save configuration data to a file.
- `load_data`: Load data from a file.
- `save_data`: Save data to a file.
- `setup_logging`: Initialize and configure the logging system.

"""

from .config import load_config, save_config
from .data import load_data, save_data
from .logging import setup_logging

__all__ = ["load_config", "load_data", "save_config", "save_data", "setup_logging"]

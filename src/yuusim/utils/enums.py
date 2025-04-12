"""
`enums.py` Module Documentation
===============================

Overview
--------
This module defines custom enumerations used throughout the `yuusim` package. Enumerations provide a
way to define a set of named constants, which helps in writing more readable and maintainable code.
By using enumerations, the code becomes more self - explanatory and less error - prone when dealing
with specific values or states.

Key Enumerations
----------------
- `DataCompression`: Defines different data compression algorithms that can be used when storing data.
  It provides options for applying compression to improve storage efficiency or choosing to store data
  without compression.
- `LogLevel`: Maps human - readable log level names to the corresponding integer values used by the
  Loguru logging library. This ensures consistent log level configuration across the application,
  making it easier to manage and filter log messages.

Usage Examples
--------------
### Using DataCompression
```python
from yuusim.utils.enums import DataCompression

# Choose GZIP compression for data storage
compression_method = DataCompression.GZIP
```
"""

from enum import Enum

__all__ = [
    "DataCompression",
    "LogLevel",
]


class DataCompression(Enum):
    """
    Enumeration for data compression algorithms.

    This enumeration defines various compression algorithms available for data storage.
    Each member corresponds to a specific compression method, and the `NONE` member
    indicates that the data should be stored without compression.

    Attributes
    ----------
    GZIP : str
        Represents the GZIP compression algorithm, a widely-used lossless compression method.
    LZF : str
        Represents the LZF compression algorithm, known for its fast compression and decompression speed.
    NONE : None
        Indicates that no compression should be applied to the data.
    """

    GZIP = "gzip"
    LZF = "lzf"
    NONE = None


class LogLevel(Enum):
    """
    Enumeration for log levels corresponding to Loguru's logging system.

    This enumeration maps user-friendly log level names to their respective integer values
    used by the Loguru logging library. It ensures consistent log level configuration
    throughout the application.

    Attributes
    ----------
    DEBUG : int
        Debug level. Used to provide detailed information for debugging purposes.
    INFO : int
        Informational level. Used to present general information about the application's state.
    SUCCESS : int
        Success level. Indicates that an operation has completed successfully. Added as Loguru supports it.
    WARNING : int
        Warning level. Indicates potential issues that may not cause the application to fail.
    ERROR : int
        Error level. Indicates that an error has occurred, but the application can still continue.
    CRITICAL : int
        Critical level. Indicates a severe error that may lead to the application termination.
    """

    DEBUG = 10
    INFO = 20
    SUCCESS = 25  # Added SUCCESS level as loguru has it
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

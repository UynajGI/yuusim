from enum import Enum

__all__ = [
    "DataCompression",
    "LogLevel",
]


class DataCompression(Enum):
    """
    Enum for compression algorithms.

    This enum represents different compression algorithms that can be used for data storage.
    The `NONE` member indicates that no compression should be applied.
    """

    GZIP = "gzip"
    LZF = "lzf"
    NONE = None


class LogLevel(Enum):
    """
    Enum for log levels corresponding to loguru's log levels.

    This enum maps human - readable log levels to their corresponding integer values used by loguru.
    It helps in setting consistent log levels across the application.
    """

    DEBUG = 10
    INFO = 20
    SUCCESS = 25  # Added SUCCESS level as loguru has it
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

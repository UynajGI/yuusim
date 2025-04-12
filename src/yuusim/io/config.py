"""
`config.py` Module Documentation
================================

Overview
--------
This module serves as a comprehensive solution for handling configuration files in multiple formats.
It simplifies the process of loading and saving configuration data, while also ensuring data integrity
through validation and error handling mechanisms.

Supported File Formats
----------------------
- **TOML**: A human - readable configuration file format. Ideal for configurations that require a simple
  and intuitive structure.
- **JSON**: A lightweight data interchange format. Widely used for its simplicity and compatibility
  across different programming languages.
- **YAML**: A human - friendly data serialization language. It supports complex data structures and
  is often used for configuration files due to its readability.

Key Features
------------
1. **File I/O Operations**: The module provides functions to load configuration data from files and
   save configuration data to files in the supported formats.
2. **Validation**: It validates the configuration data to ensure that it contains the required 'system'
   field, maintaining the consistency of the configuration.
3. **Error Handling**: The module includes custom exception classes to handle various error scenarios,
   such as unsupported file formats, missing configuration files, and invalid configuration data.

Module Functions
----------------
- `_check_file_format`: Checks if the specified file format is supported.
- `_force_path`: Converts a path - like object to an absolute `Path` object.
- `_validate_config`: Validates if the configuration dictionary contains the 'system' field.
- `load_config`: Loads configuration data from a file in the specified format.
- `save_config`: Saves the configuration data to a file in the specified format.

Usage Examples
--------------
### Loading a Configuration File
```python
from yuusim.io.config import load_config
config = load_config('path/to/config.toml')
```
"""

import json
from pathlib import Path
from typing import Any, cast

import toml
import yaml
from loguru import logger

# Import custom exception classes
from yuusim.utils.exceptions import ConfigurationError, UnsupportedFileFormatError
from yuusim.utils.typing import DictLike, DumpFunc, LoadFunc, PathLike

# Supported file formats
SUPPORTED_FORMATS: dict[str, tuple[LoadFunc, DumpFunc]] = {
    "toml": (cast(LoadFunc, toml.load), cast(DumpFunc, toml.dump)),
    "json": (
        cast(LoadFunc, json.load),
        cast(DumpFunc, lambda data, f: json.dump(data, f, indent=4, ensure_ascii=False)),
    ),
    "yaml": (cast(LoadFunc, yaml.safe_load), cast(DumpFunc, lambda data, f: yaml.safe_dump(data, f))),
}


def _check_file_format(file_format: str) -> None:
    """
    Check if the specified file format is supported.

    Parameters
    ----------
    file_format : str
        The file format to check, typically the file extension without the dot.

    Raises
    ------
    UnsupportedFileFormatError
        If the provided file format is not in the list of supported formats.
    """
    if file_format not in SUPPORTED_FORMATS:
        raise UnsupportedFileFormatError(file_format, list(SUPPORTED_FORMATS.keys()))


def _force_path(filename: PathLike) -> Path:
    """
    Convert the input path-like object to a `Path` object and ensure it is an absolute path.

    Parameters
    ----------
    filename : PathLike
        A path-like object, which can be either a string or a `Path` object.

    Returns
    -------
    Path
        An absolute `Path` object representing the input path.
    """
    if isinstance(filename, str):
        filename = Path(filename)
    return filename.absolute()


def _validate_config(config: DictLike) -> None:
    """
    Validate if the configuration dictionary contains the 'system' field.

    Parameters
    ----------
    config : DictLike
        A dictionary representing the configuration data.

    Raises
    ------
    ConfigurationError
        If the 'system' field is missing from the configuration dictionary.
    """
    if "system" not in config:
        error_msg = "Configuration must contain the 'system' field."
        logger.error(error_msg)
        raise ConfigurationError(error_msg)


def load_config(config_file: PathLike) -> Any:
    """
    Load configuration data from a file in the specified format.

    Parameters
    ----------
    config_file : PathLike
        Path to the configuration file, which can be either a string or a `Path` object.

    Returns
    -------
    Any
        A dictionary containing the configuration data.

    Raises
    ------
    ConfigurationError
        If the configuration file does not exist or does not contain the 'system' field.
    UnsupportedFileFormatError
        If the specified file format is not supported.
    Exception
        Exceptions from the corresponding parser, such as `toml.TomlDecodeError`,
        `json.JSONDecodeError`, or `yaml.YAMLError`.
    """
    config_file = _force_path(config_file)
    file_format = config_file.suffix.lstrip(".").lower()
    _check_file_format(file_format)
    if not config_file.exists():
        error_msg = f"Configuration file not found: {config_file}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg)

    try:
        load_func = SUPPORTED_FORMATS[file_format][0]
        with open(config_file, encoding="utf-8") as f:
            config = load_func(f)
        _validate_config(config)
        logger.success(f"Successfully loaded configuration file: {config_file}, format: {file_format}")
    except Exception as e:
        logger.error(f"Failed to load configuration file: {config_file}, format: {file_format} - {e!s}")
        raise

    return config


def save_config(config: DictLike, filename: PathLike, file_format: str = "toml", force: bool = False) -> None:
    """
    Save the configuration data to a file in the specified format.

    Parameters
    ----------
    config : DictLike
        A dictionary containing the configuration data to be saved.
    filename : PathLike
        Path to the configuration file, which can be either a string or a `Path` object.
    file_format : str, optional
        The file format to save the configuration in. Options are 'toml', 'json', 'yaml'.
        Default is 'toml'.
    force : bool, optional
        Whether to force overwrite an existing file. Default is False.

    Raises
    ------
    PermissionError
        If there is no permission to write to the file.
    UnsupportedFileFormatError
        If the specified file format is not supported.
    ConfigurationError
        If the configuration does not contain the 'system' field.
    Exception
        Exceptions from the corresponding parser, such as `toml.TomlDecodeError`,
        `json.JSONDecodeError`, or `yaml.YAMLError`.
    """
    filename = _force_path(filename)
    _check_file_format(file_format)
    _validate_config(config)
    filename = filename.with_suffix(f".{file_format}")

    if not force and filename.exists():
        logger.warning(f"Configuration file already exists: {filename}")

    try:
        filename.parent.mkdir(parents=True, exist_ok=True)
        dump_func = SUPPORTED_FORMATS[file_format][1]
        with open(filename, "w", encoding="utf-8") as f:
            dump_func(config, f)
        logger.info(f"Configuration saved to: {filename}, format: {file_format}")
    except PermissionError as e:
        logger.error(f"Permission denied when writing configuration file: {filename}, format: {file_format} - {e!s}")
        raise
    except Exception as e:
        logger.error(f"Failed to save configuration file: {filename}, format: {file_format} - {e!s}")
        raise

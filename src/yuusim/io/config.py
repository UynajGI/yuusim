import json
from pathlib import Path
from typing import Any

import toml
import yaml
from loguru import logger

# 导入自定义异常类
from yuusim.utils.exceptions import ConfigurationError, UnsupportedFileFormatError
from yuusim.utils.typing import DictLike, PathLike

# 支持的文件格式
SUPPORTED_FORMATS = {
    "toml": (toml.load, toml.dump),
    "json": (json.load, lambda data, f: json.dump(data, f, indent=4)),
    "yaml": (yaml.safe_load, lambda data, f: yaml.safe_dump(data, f)),
}


def _check_file_format(file_format: str) -> None:
    """
    Check if the file format is supported.
    """
    if file_format not in SUPPORTED_FORMATS:
        raise UnsupportedFileFormatError(file_format, list(SUPPORTED_FORMATS.keys()))


def _force_path(filename: PathLike) -> Path:
    """
    Convert the input path to a Path object and ensure it is an absolute path.
    """
    if isinstance(filename, str):
        filename = Path(filename)
    return filename.absolute()


def _validate_config(config: DictLike) -> None:
    """
    Validate if the configuration contains the 'system' field.
    """
    if "system" not in config:
        error_msg = "Configuration must contain the 'system' field."
        logger.error(error_msg)
        raise ConfigurationError(error_msg)


def load_config(config_file: PathLike) -> Any:
    """
    Load configuration from a file in the specified format.

    Args:
        config_file: Path to the configuration file.

    Returns:
        A dictionary containing the configuration.

    Raises:
        ConfigurationError: If the configuration file does not exist or does not contain the 'system' field.
        UnsupportedFileFormatError: If the specified file format is not supported.
        Exceptions from the corresponding parser: such as toml.TomlDecodeError, json.JSONDecodeError, yaml.YAMLError.
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
            config = load_func(f)  # type: ignore[call-arg]
        _validate_config(config)
        logger.success(f"Successfully loaded configuration file: {config_file}, format: {file_format}")
    except Exception as e:
        logger.error(f"Failed to load configuration file: {config_file}, format: {file_format} - {e!s}")
        raise

    return config


def save_config(config: DictLike, filename: PathLike, file_format: str = "toml", force: bool = False) -> None:
    """
    Save the configuration to a file in the specified format.

    Args:
        config: Configuration dictionary.
        filename: Path to the configuration file.
        file_format: File format, options are 'toml', 'json', 'yaml', default is 'toml'.
        force: Whether to force overwrite an existing file.

    Raises:
        PermissionError: If there is no permission to write to the file.
        UnsupportedFileFormatError: If the specified file format is not supported.
        ConfigurationError: If the configuration does not contain the 'system' field.
        Exceptions from the corresponding parser: such as toml.TomlDecodeError, json.JSONDecodeError, yaml.YAMLError.
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
            dump_func(config, f)  # type: ignore[call-arg]
        logger.info(f"Configuration saved to: {filename}, format: {file_format}")
    except PermissionError as e:
        logger.error(f"Permission denied when writing configuration file: {filename}, format: {file_format} - {e!s}")
        raise
    except Exception as e:
        logger.error(f"Failed to save configuration file: {filename}, format: {file_format} - {e!s}")
        raise

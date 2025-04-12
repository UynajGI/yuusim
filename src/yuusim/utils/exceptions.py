__all__ = [
    "ConfigurationError",
    "DataFileNotFoundError",
    "DataLoadError",
    "DataSaveError",
    "LoggingConfigurationError",
    "MissingRequiredParametersError",
    "UnsupportedFileFormatError",
]

from typing import Union

from .typing import PathLike


class ConfigurationError(Exception):
    """
    This exception is raised when there are issues with configuration-related operations,
    such as the configuration file not being found or having an incorrect format.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnsupportedFileFormatError(ValueError):
    """
    This exception is raised when an unsupported file format is used for loading or saving configuration files.
    """

    def __init__(self, file_format: str, supported_formats: list[str]) -> None:
        message = f"Unsupported file format: {file_format}, supported formats are: {', '.join(supported_formats)}"
        super().__init__(message)


class DataFileNotFoundError(FileNotFoundError):
    """
    This exception is raised when trying to load a data file, but the file does not exist.
    """

    def __init__(self, file_path: PathLike) -> None:
        message = f"Data file not found: {file_path}"
        super().__init__(message)


class LoggingConfigurationError(Exception):
    """
    This exception is raised when the logging system configuration fails.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingRequiredParametersError(ValueError):
    """
    This exception is raised when, during parameter validation, it is found that required parameters are missing.
    """

    def __init__(self, missing_params: Union[list[str], str]) -> None:
        message = f"Missing required parameters: {missing_params}"
        super().__init__(message)


class DataSaveError(Exception):
    """
    This exception is raised when an error occurs while saving data to a file,
    such as permission issues or file write errors.
    """

    def __init__(self, file_path: PathLike, error: str) -> None:
        message = f"Failed to save data: {file_path} - {error}"
        super().__init__(message)


class DataLoadError(Exception):
    """
    This exception is raised when an error occurs while loading data from a file,
    such as incorrect file format or a corrupted file.
    """

    def __init__(self, file_path: PathLike, error: str) -> None:
        message = f"Failed to load data: {file_path} - {error}"
        super().__init__(message)

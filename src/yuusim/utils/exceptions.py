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
    Exception raised when there are issues with configuration-related operations.

    This can include scenarios such as the configuration file not being found
    or having an incorrect format.

    Parameters
    ----------
    message : str
        A descriptive message explaining the configuration issue.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnsupportedFileFormatError(ValueError):
    """
    Exception raised when an unsupported file format is used for loading or saving configuration files.

    Parameters
    ----------
    file_format : str
        The unsupported file format that was attempted to be used.
    supported_formats : list[str]
        A list of supported file formats.
    """

    def __init__(self, file_format: str, supported_formats: list[str]) -> None:
        message = f"Unsupported file format: {file_format}, supported formats are: {', '.join(supported_formats)}"
        super().__init__(message)


class DataFileNotFoundError(FileNotFoundError):
    """
    Exception raised when trying to load a data file, but the file does not exist.

    Parameters
    ----------
    file_path : PathLike
        The path to the data file that was not found.
    """

    def __init__(self, file_path: PathLike) -> None:
        message = f"Data file not found: {file_path}"
        super().__init__(message)


class LoggingConfigurationError(Exception):
    """
    Exception raised when the logging system configuration fails.

    Parameters
    ----------
    message : str
        A descriptive message explaining the logging configuration failure.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MissingRequiredParametersError(ValueError):
    """
    Exception raised when, during parameter validation, required parameters are found to be missing.

    Parameters
    ----------
    missing_params : Union[list[str], str]
        The name(s) of the missing required parameters. Can be a single string or a list of strings.
    """

    def __init__(self, missing_params: Union[list[str], str]) -> None:
        message = f"Missing required parameters: {missing_params}"
        super().__init__(message)


class DataSaveError(Exception):
    """
    Exception raised when an error occurs while saving data to a file.

    This can include issues such as permission problems or file write errors.

    Parameters
    ----------
    file_path : PathLike
        The path to the file where data was attempted to be saved.
    error : str
        A description of the error that occurred during the save operation.
    """

    def __init__(self, file_path: PathLike, error: str) -> None:
        message = f"Failed to save data: {file_path} - {error}"
        super().__init__(message)


class DataLoadError(Exception):
    """
    Exception raised when an error occurs while loading data from a file.

    This can include issues such as incorrect file format or a corrupted file.

    Parameters
    ----------
    file_path : PathLike
        The path to the file from which data was attempted to be loaded.
    error : str
        A description of the error that occurred during the load operation.
    """

    def __init__(self, file_path: PathLike, error: str) -> None:
        message = f"Failed to load data: {file_path} - {error}"
        super().__init__(message)

"""
`data.py` Module Documentation
==============================

This module provides a set of functions for saving and loading data along with its metadata.
It supports specific file formats, with the primary focus on HDF5. The module includes
error handling and validation to ensure the integrity of the data during I/O operations.

Supported File Formats
----------------------
- HDF5 (`.hdf5` and `.h5` extensions)

Key Functions
-------------
- `save_data`: Saves data and metadata to a file in a specified format.
- `load_data`: Loads data and metadata from a file.

"""

import json
from pathlib import Path
from typing import Any, Optional

import h5py
import numpy as np
from loguru import logger
from numpy.typing import NDArray

from yuusim.utils.exceptions import DataLoadError, DataSaveError, UnsupportedFileFormatError
from yuusim.utils.typing import ArrayLike, Metadatadict, PathLike

SUPPORTED_FORMATS = {
    "hdf5": (h5py.File, h5py.File),
    "h5": (h5py.File, h5py.File),
}


def save_data(
    data: ArrayLike, filename: PathLike, metadata: Metadatadict, file_format: str = "h5", **kwargs: Any
) -> None:
    """
    Save data and metadata to a file.

    Parameters
    ----------
    data : ArrayLike
        The data to save, which can be a NumPy array, list, or tuple.
    filename : PathLike
        The target file path, either a string or a `pathlib.Path` object.
    metadata : Metadatadict
        Metadata associated with the data. It must contain the 'system' key.
    file_format : str, optional
        The file format to use, defaulting to "h5".
    **kwargs : Any
        Additional keyword arguments passed to the underlying save functions.

    Raises
    ------
    ValueError
        If the metadata does not contain the 'system' key.
    UnsupportedFileFormatError
        If the specified file format is not supported.
    DataSaveError
        If an error occurs during the data saving process.
    """
    if "system" not in metadata:
        error_msg = "Metadata must contain 'system' key."
        logger.error(error_msg)
        raise ValueError(error_msg)
    filename = filename if isinstance(filename, Path) else Path(filename)
    file_format = file_format.lower()
    filename = filename.with_suffix(f".{file_format}")
    data = np.asarray(data)
    _save_data(filename, data, metadata, file_format, **kwargs)


def _save_data(filename: Path, data: NDArray, metadata: Metadatadict, file_format: str, **kwargs: Any) -> None:
    """
    Internally handle data saving based on the specified format.

    Parameters
    ----------
    filename : Path
        Target file path.
    data : NDArray
        Data to save.
    metadata : Metadatadict
        Associated metadata.
    file_format : str
        File format to use.
    **kwargs : Any
        Additional arguments.
    """
    if file_format not in SUPPORTED_FORMATS:
        logger.error(f"Unsupported file format: {file_format}")
        raise UnsupportedFileFormatError(file_format=file_format, supported_formats=list(SUPPORTED_FORMATS.keys()))

    try:
        if file_format in {"hdf5", "h5"}:
            _save_hdf5(filename, data, metadata, **kwargs)
        logger.success(f"Successfully saved data to {filename} in {file_format} format.")
    except Exception as e:
        logger.error(f"Failed to save data to {filename}: {e}")
        raise DataSaveError(file_path=filename, error=str(e)) from e


def _save_hdf5(filename: Path, data: NDArray, metadata: Metadatadict, **kwargs: Any) -> None:
    """
    Save data and metadata to an HDF5 file.

    Parameters
    ----------
    filename : Path
        HDF5 file path.
    data : NDArray
        Data to save.
    metadata : Metadatadict
        Metadata to save as attributes.
    **kwargs : Any
        Arguments for dataset creation.
    """
    with h5py.File(filename, "w") as f:
        if metadata:
            for key, value in metadata.items():
                try:
                    serialized_value = json.dumps(value)
                    f.attrs[key] = serialized_value
                except (TypeError, ValueError):
                    f.attrs[key] = str(value)
        f.create_dataset(
            "data",
            data=data,
            chunks=True if data.size > 1000000 else None,
            compression=kwargs.get("compression", "gzip"),
            compression_opts=kwargs.get("compression_opts"),
            shuffle=kwargs.get("shuffle", True),
        )


def load_data(path: Path) -> Optional[tuple[NDArray, Optional[Metadatadict]]]:
    """
    Load data and metadata from a file.

    Parameters
    ----------
    path : Path
        The path to the file.

    Returns
    -------
    Optional[tuple[NDArray, Optional[Metadatadict]]]
        A tuple containing the data and metadata, or `None` if an error occurs.

    Raises
    ------
    UnsupportedFileFormatError
        If the file format is not supported.
    DataLoadError
        If an error occurs during the data loading process.
    """
    path = path if isinstance(path, Path) else Path(path)
    file_format = path.suffix.lower().lstrip(".")
    if file_format not in SUPPORTED_FORMATS:
        logger.error(f"Unsupported file format: {file_format}")
        raise UnsupportedFileFormatError(file_format=file_format, supported_formats=list(SUPPORTED_FORMATS.keys()))
    try:
        if file_format in {"hdf5", "h5"}:
            return _load_hdf5(path)
    except Exception as e:
        logger.error(f"Failed to load data from {path}: {e}")
        raise DataLoadError(file_path=path, error=str(e)) from e
    return None


def _parse_and_validate_metadata(metadata: Metadatadict, path: Path) -> Metadatadict:
    """Parse and validate 'system' and 'parameters' in metadata."""
    try:
        if "system" in metadata:
            metadata["system"] = (
                json.loads(metadata["system"]) if isinstance(metadata["system"], str) else metadata["system"]
            )
        if "parameters" in metadata:
            metadata["parameters"] = (
                json.loads(metadata["parameters"])
                if isinstance(metadata["parameters"], str)
                else metadata["parameters"]
            )
    except (KeyError, json.JSONDecodeError) as e:
        logger.warning(f"Failed to parse 'system' or 'parameters' in metadata of {path} as JSON.")
        error_msg = "Failed to parse 'system' or 'parameters' in metadata as JSON."
        raise DataLoadError(file_path=path, error=error_msg) from e

    if "system" not in metadata:
        logger.error(f"Metadata must contain 'system' key in {path}.")
        raise DataLoadError(file_path=path, error="Metadata must contain 'system' key.")

    return metadata


def _load_hdf5(path: Path) -> tuple[NDArray, Optional[Metadatadict]]:
    """Load data and metadata from an HDF5 file."""
    with h5py.File(path, "r") as f:
        data = np.asarray(f["data"])
        metadata = dict(f.attrs)
        metadata = _parse_and_validate_metadata(metadata, path)
        return data, metadata

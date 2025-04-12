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
    """Save data and metadata to a file.

    Args:
        filename: The filename to save the data to.
        data: The data to save.
        metadata: The metadata to save.
        file_format: The file format to use. Defaults to "hdf5".

    Raises:
        UnsupportedFileFormatError: If the file format is not supported.
        DataSaveError: If the data could not be saved.
        ValueError: If metadata does not contain 'system' key.
    """
    # 检查 metadata 是否包含 'system'
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
    """Internal function to save data based on the specified format."""

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
    """Save data and metadata to an HDF5 file."""
    with h5py.File(filename, "w") as f:
        if metadata:
            for key, value in metadata.items():
                try:
                    # Serialize the value using JSON
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
    """Load data and metadata from a file.

    Args:
        path: The path to the file.

    Returns:
        A tuple containing the data and metadata.
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


def _parse_and_validate_metadata(metadata: Metadatadict, path: Path) -> Metadatadict:
    """
    Parse the 'system' and 'parameters' fields in the metadata and validate the presence of the 'system' field.
    """
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
        logger.error(f"Metadata must contain'system' key in {path}.")
        raise DataLoadError(file_path=path, error="Metadata must contain 'system' key.")

    return metadata


def _load_hdf5(path: Path) -> tuple[NDArray, Optional[Metadatadict]]:
    """Load data and metadata from an HDF5 file."""
    with h5py.File(path, "r") as f:
        data = np.asarray(f["data"])
        metadata = dict(f.attrs)
        metadata = _parse_and_validate_metadata(metadata, path)
        return data, metadata

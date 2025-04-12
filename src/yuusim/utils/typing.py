from pathlib import Path
from typing import Any, Protocol, Union

from numpy.typing import NDArray

__all__ = [
    "ArrayLike",
    "DictLike",
    "EnvDirs",
    "Metadatadict",
    "ParamHash",
    "ParameterGrid",
    "PathLike",
    "SimulationEnvironmentProtocol",
    "Timestamp",
]

PathLike = Union[str, Path]
DictLike = dict[str, Any]
ArrayLike = Union[NDArray[Any], list[Any], tuple[Any, ...]]
Metadatadict = dict[str, Any]
EnvDirs = dict[str, Path]
ParamHash = str
Timestamp = str
ParameterGrid = dict[str, NDArray]


class SimulationEnvironmentProtocol(Protocol):
    project_name: str
    config: DictLike
    dirs: EnvDirs
    param_hash: ParamHash
    timestamp: Timestamp

    def _initialize_folders(self) -> None: ...
    def cleanup(self) -> None: ...
    def setup(self, config_path: PathLike, **kwargs) -> None: ...

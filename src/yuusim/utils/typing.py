"""
This module defines custom type hints and protocols used throughout the `yuusim` package.
These type definitions enhance code readability, maintainability, and enable better type checking.

Overview
--------
The `typing.py` module serves as a central location for all custom type definitions in the `yuusim` package.
It provides type aliases for common data structures and a protocol for the simulation environment.
These type definitions are used across the package to make the code more self - explanatory and to catch
type - related errors early during development.

Type Aliases
------------
- `PathLike`: Represents a path - like object, which can be either a string or a `pathlib.Path` object.
- `DictLike`: Represents a dictionary with string keys and values of any type.
- `ArrayLike`: Represents an array - like object, such as a NumPy array, Python list, or tuple.
- `Metadatadict`: Represents a dictionary used to store metadata.
- `EnvDirs`: Represents a dictionary that maps directory names to `pathlib.Path` objects.
- `ParamHash`: Represents a string that stores the hash value of simulation parameters.
- `Timestamp`: Represents a string that stores the time when a simulation starts or ends.
- `ParameterGrid`: Represents a dictionary where keys are parameter names and values are NumPy arrays.

Protocol
--------
- `SimulationEnvironmentProtocol`: Defines the interface for a simulation environment class. It specifies
  the required attributes and methods that a simulation environment class should implement.

Benefits
--------
- **Readability**: Type hints make the code more self - explanatory, as they clearly indicate the expected
  types of variables and function arguments.
- **Maintainability**: Centralizing type definitions in one module makes it easier to manage and update
  type information across the package.
- **Type Checking**: Static type checkers can use these type hints to catch type - related errors early,
  reducing the likelihood of runtime errors.

Usage Examples
--------------
### Using PathLike
```python
from yuusim.utils.typing import PathLike

def read_file(path: PathLike):
    # Function implementation
    pass

read_file('example.txt')  # Using a string
from pathlib import Path
read_file(Path('example.txt'))  # Using a Path object
```
"""

from pathlib import Path
from typing import Any, Callable, Protocol, TextIO, Union

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
"""
A type alias representing a path-like object. It can be either a string or a `pathlib.Path` object.
This is useful when a function can accept either a string path or a `Path` object.
"""

DictLike = dict[str, Any]
"""
A type alias representing a dictionary with string keys and values of any type.
This is a generic type hint for dictionaries where the key type is known to be a string.
"""

ArrayLike = Union[NDArray[Any], list[Any], tuple[Any, ...]]
"""
A type alias representing an array-like object. It can be a NumPy array, a Python list, or a tuple.
This is useful when a function can accept different types of array-like inputs.
"""

Metadatadict = dict[str, Any]
"""
A type alias representing a dictionary used to store metadata. It has string keys and values of any type.
This is typically used to store additional information about data, such as simulation parameters.
"""

EnvDirs = dict[str, Path]
"""
A type alias representing a dictionary that maps directory names (strings) to `pathlib.Path` objects.
This is used to store the paths of different directories in the simulation environment.
"""

ParamHash = str
"""
A type alias representing a parameter hash. It is a string that typically stores the hash value of simulation parameters.
This hash can be used to identify a specific set of simulation parameters.
"""

Timestamp = str
"""
A type alias representing a timestamp. It is a string that typically stores the time when a simulation starts or ends.
The format of the timestamp can vary depending on the application.
"""

ParameterGrid = dict[str, NDArray]
"""
A type alias representing a parameter grid. It is a dictionary where the keys are parameter names (strings)
and the values are NumPy arrays. This is used to define a grid of parameters for a simulation.
"""

LoadFunc = Callable[[TextIO], DictLike]
"""
A type alias representing a function that loads data from a file-like object.
It takes a file-like object as input and returns a dictionary-like object.
"""

DumpFunc = Callable[[DictLike, TextIO], None]
"""
A type alias representing a function that dumps data to a file-like object.
It takes a dictionary-like object and a file-like object as input and returns nothing.
"""


class SimulationEnvironmentProtocol(Protocol):
    """
    A protocol defining the interface for a simulation environment class.

    This protocol specifies the required attributes and methods that a simulation environment class
    should implement. It is used for type checking and to ensure that different simulation environment
    implementations adhere to a common interface.

    Attributes
    ----------
    project_name : str
        The name of the simulation project.
    config : DictLike
        A dictionary containing the configuration parameters for the simulation.
    dirs : EnvDirs
        A dictionary mapping directory names to their corresponding `pathlib.Path` objects.
    param_hash : ParamHash
        A string representing the hash of the simulation parameters.
    timestamp : Timestamp
        A string representing the timestamp when the simulation started.

    Methods
    -------
    _initialize_folders() -> None
        Initialize the necessary folders for the simulation environment.
    cleanup() -> None
        Clean up the resources used by the simulation environment, such as temporary files.
    setup(config_path: PathLike, **kwargs) -> None
        Set up the simulation environment using the configuration file at the given path.
        Additional keyword arguments can be provided for custom configuration.
    """

    project_name: str
    config: DictLike
    dirs: EnvDirs
    param_hash: ParamHash
    timestamp: Timestamp

    def _initialize_folders(self) -> None:
        """
        Initialize the necessary folders for the simulation environment.

        This method should create all the required directories specified in the `dirs` attribute.
        """
        ...

    def cleanup(self) -> None:
        """
        Clean up the resources used by the simulation environment.

        This method should remove any temporary files or directories created during the simulation.
        """
        ...

    def setup(self, config_path: PathLike, **kwargs: Any) -> None:
        """
        Set up the simulation environment using the configuration file at the given path.

        This method should load the configuration from the specified file and initialize the
        simulation environment accordingly. Additional keyword arguments can be provided for
        custom configuration.

        Parameters
        ----------
        config_path : PathLike
            The path to the configuration file, which can be either a string or a `pathlib.Path` object.
        **kwargs : Any
            Additional keyword arguments for custom configuration.
        """
        ...

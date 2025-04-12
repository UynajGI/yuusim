"""
`yuusim.utils` Module Documentation
===================================

Overview
--------
The `yuusim.utils` module serves as a collection of utility components that enhance the functionality,
robustness, and maintainability of the `yuusim` project. It encapsulates various sub - modules, each
targeting specific utility aspects such as custom enumerations, exception handling, performance analysis,
and type definitions. These utilities are designed to be reusable across different parts of the project,
promoting code modularity and reducing redundancy.

Sub - Modules
-------------
- `enums`: Defines custom enumerations for consistent and type - safe usage of values like data compression
  algorithms and log levels throughout the project.
- `exceptions`: Houses custom exception classes. These exceptions provide more detailed and project - specific
  error information, making it easier to debug and handle errors in a meaningful way.
- `optimize`: Contains classes and functions for performance analysis, such as estimating memory and time
  usage of simulation functions. It helps in identifying performance bottlenecks and optimizing the simulation
  process.
- `typing`: Offers custom type definitions and type aliases. These type hints improve code readability,
  enable better static type checking, and make the codebase more self - explanatory.

Usage
-----
To use the utilities provided by this module, you can import the relevant sub - modules or specific
components as needed. For example:

```python
from yuusim.utils.enums import LogLevel
from yuusim.utils.exceptions import ConfigurationError

try:
    # Some code that might raise a configuration error
    pass
except ConfigurationError as e:
    print(f"Configuration error occurred: {e}")
```
"""

from . import enums, exceptions, typing

__all__ = [
    "enums",
    "exceptions",
    "typing",
]

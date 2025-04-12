"""
`optimize.py` Module Documentation
==================================

Overview
--------
This module offers comprehensive functionality for evaluating the memory and time performance of Python functions.
It provides a structured approach to profiling functions, generating detailed reports, and helping developers
identify performance bottlenecks in their code.

Key Components
--------------
1. **Memory and Time Reports**: Two data classes, `MemoryReport` and `TimeReport`, are defined to store and present
   the results of memory and time profiling respectively. These classes offer a convenient way to access and display
   performance metrics.
2. **Profiling Class**: The `OptimizeAnalysis` class serves as the core component for performing memory and time
   analysis on a given function. It encapsulates the logic for running the function, collecting metrics, and
   generating reports.

Supported Profiling Tools
-------------------------
- **`memory_profiler`**: Used to measure the memory usage of a function. It provides detailed information about
  peak, average, and base memory consumption.
- **`cProfile`**: A built - in Python module for profiling the time performance of a function. It offers insights
  into the total execution time, number of calls, and cumulative time spent in the function.

Usage Examples
--------------
### Analyzing Memory Usage
```python
from yuusim.utils.optimize import OptimizeAnalysis

def example_function():
    data = [i for i in range(100000)]
    return data

analyzer = OptimizeAnalysis(example_function)
memory_report = analyzer.analyze_memory()
print(memory_report)
```
"""

import cProfile
import io
import pstats
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from memory_profiler import memory_usage

T = TypeVar("T")


@dataclass
class MemoryReport:
    """
    Represents a memory usage report for a function.

    Attributes
    ----------
    peak_memory : float
        The peak memory usage in MiB.
    average_memory : float
        The average memory usage in MiB.
    base_memory : float
        The base memory usage in MiB.
    total_samples : int
        The total number of memory samples taken.
    raw_measurements : list[float]
        The raw memory usage measurements.

    Methods
    -------
    __str__()
        Returns a string representation of the memory usage report.
    """

    peak_memory: float
    average_memory: float
    base_memory: float
    total_samples: int
    raw_measurements: list[float]

    def __str__(self) -> str:
        """
        Returns a string representation of the memory usage report.
        """
        return (
            f"Memory Usage Report:\n"
            f"Peak Memory Usage: {self.peak_memory:.2f} MiB\n"
            f"Average Memory Usage: {self.average_memory:.2f} MiB\n"
            f"Base Memory Usage: {self.base_memory:.2f} MiB\n"
            f"Total Samples: {self.total_samples}\n"
        )


@dataclass
class TimeReport:
    """
    Represents a time performance report for a function.

    Attributes:
        total_time (float): The total execution time in seconds.
        calls (int): The number of calls to the function.
        time_per_call (float): The average time per call in seconds.
        cumulative_time (float): The cumulative execution time in seconds.
        function_name (str): The name of the function.
        detailed_stats (str): The detailed profiling statistics.
    """

    total_time: float
    calls: int
    time_per_call: float
    cumulative_time: float
    function_name: str
    detailed_stats: str

    def __str__(self) -> str:
        """
        Return a string representation of the memory usage report.

        Returns
        -------
        str
            A formatted string containing the peak, average, and base memory usage,
            as well as the total number of samples.
        """
        return (
            f"Time Performance Report:\n"
            f"Function Name: {self.function_name}\n"
            f"Total Execution Time: {self.total_time:.4f} seconds\n"
            f"Number of Calls: {self.calls}\n"
            f"Average Time per Call: {self.time_per_call:.4f} seconds\n"
            f"Cumulative Time: {self.cumulative_time:.4f} seconds\n"
            f"\nDetailed Statistics:\n{self.detailed_stats}"
        )


class OptimizeAnalysis:
    """
    A class for analyzing the memory and time performance of a function.

    Attributes
    ----------
    func : Callable[..., T]
        The function to be analyzed.
    func_name : str
        The name of the function.

    Methods
    -------
    analyze_memory(*args, **kwargs)
        Analyzes the memory usage of the function and returns a detailed report.
    analyze_time(*args, **kwargs)
        Analyzes the time performance of the function and returns a detailed report.
    """

    def __init__(self, func: Callable[..., T]) -> None:
        """
        Initialize the OptimizeAnalysis class.

        Parameters
        ----------
        func : Callable[..., T]
            The function to be analyzed.
        """
        self.func = func
        self.func_name = func.__name__

    def analyze_memory(self, *args: Any, **kwargs: Any) -> MemoryReport:
        """
        Analyze the memory usage of the function and return a detailed report.

        Parameters
        ----------
        *args : Any
            Positional arguments to pass to the function.
        **kwargs : Any
            Keyword arguments to pass to the function.

        Returns
        -------
        MemoryReport
            A report object containing memory usage statistics.
        """

        def wrapped() -> Any:
            return self.func(*args, **kwargs)

        # Bug fix: Changed the parameter passing to the function, and now it calls the wrapped function directly
        measurements: list[float] = memory_usage(wrapped, backend="psutil", interval=0.1, max_iterations=100)

        return MemoryReport(
            peak_memory=max(measurements),
            average_memory=sum(measurements) / len(measurements),
            base_memory=measurements[0],
            total_samples=len(measurements),
            raw_measurements=measurements,
        )

    def analyze_time(self, *args: Any, **kwargs: Any) -> TimeReport:
        """
        Analyze the time performance of the function and return a detailed report.

        Parameters
        ----------
        *args : Any
            Positional arguments to pass to the function.
        **kwargs : Any
            Keyword arguments to pass to the function.

        Returns
        -------
        TimeReport
            A report object containing time performance statistics.
        """
        pr = cProfile.Profile()
        pr.enable()
        self.func(*args, **kwargs)
        pr.disable()

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats("tottime")
        ps.print_stats()

        # Get the statistics of the main function
        for func_stats in ps.stats.items():  # type: ignore  # noqa: PGH003
            if self.func_name in str(func_stats[0]):
                (_, _, fn_name), (calls, _, total_time, cum_time, _) = func_stats
                return TimeReport(
                    total_time=total_time,
                    calls=calls,
                    time_per_call=total_time / calls if calls else 0,
                    cumulative_time=cum_time,
                    function_name=fn_name,
                    detailed_stats=s.getvalue(),
                )

        # If the main function statistics are not found, return an empty report
        return TimeReport(0, 0, 0, 0, self.func_name, s.getvalue())

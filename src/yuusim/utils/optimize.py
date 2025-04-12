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

    Attributes:
        peak_memory (float): The peak memory usage in MiB.
        average_memory (float): The average memory usage in MiB.
        base_memory (float): The base memory usage in MiB.
        total_samples (int): The total number of memory samples taken.
        raw_measurements (list[float]): The raw memory usage measurements.
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
        Returns a string representation of the time performance report.
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

    Attributes:
        func (Callable[..., T]): The function to be analyzed.
        func_name (str): The name of the function.
    """

    def __init__(self, func: Callable[..., T]) -> None:
        """
        Initializes the OptimizeAnalysis class.

        Args:
            func (Callable[..., T]): The function to be analyzed.
        """
        self.func = func
        self.func_name = func.__name__

    def analyze_memory(self, *args: Any, **kwargs: Any) -> MemoryReport:
        """
        Analyzes the memory usage of the function and returns a detailed report.

        Args:
            *args (Any): Positional arguments to pass to the function.
            **kwargs (Any): Keyword arguments to pass to the function.

        Returns:
            MemoryReport: A report object containing memory usage statistics.
        """

        def wrapped() -> Any:
            return self.func(*args, **kwargs)

        # Bug fix: Changed the parameter passing to the function, and now it calls the wrapped function directly
        measurements = memory_usage(wrapped, backend="psutil", interval=0.1, max_iterations=100)  # type: ignore # noqa: PGH003

        return MemoryReport(
            peak_memory=max(measurements),
            average_memory=sum(measurements) / len(measurements),
            base_memory=measurements[0],
            total_samples=len(measurements),
            raw_measurements=measurements,
        )

    def analyze_time(self, *args: Any, **kwargs: Any) -> TimeReport:
        """
        Analyzes the time performance of the function and returns a detailed report.

        Args:
            *args (Any): Positional arguments to pass to the function.
            **kwargs (Any): Keyword arguments to pass to the function.

        Returns:
            TimeReport: A report object containing time performance statistics.
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

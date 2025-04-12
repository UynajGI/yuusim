"""
`simulation.py` Module Documentation
====================================

Overview
--------
This module provides a comprehensive framework for managing and executing simulations.
It defines a `SimulationEnvironment` class that handles the initialization, configuration,
execution, and cleanup of simulation projects. Additionally, it includes a utility function
`generate_parameter_grid` to generate parameter sets for exploring the parameter space.

Key Features
------------
- **Environment Management**: Automatically creates and validates the directory structure
  for storing simulation data, logs, figures, and configurations.
- **Configuration Handling**: Loads configuration files, computes parameter hashes, and
  ensures the consistency of simulation parameters.
- **Parallel Execution**: Supports both parallel and sequential execution of simulations,
  with batch processing for improved performance.
- **Performance Analysis**: Estimates the memory and time usage of a single simulation
  run and saves the reports for further analysis.
- **Data Persistence**: Saves simulation results and configurations to files, and provides
  options for cleaning up temporary files and unused data.

Classes
-------
- `SimulationEnvironment`: Represents the simulation environment and manages all aspects
  of a simulation project.

Functions
---------
- `generate_parameter_grid`: Generates a parameter grid for exploring the parameter space
  based on the given parameter specifications.

Usage Examples
--------------
### Initialize and run a simulation
```python
from yuusim.simulation import SimulationEnvironment
import numpy as np
import time

def func(params):
    time.sleep(1)
    return np.random.rand(10)

env = SimulationEnvironment("test_project")
# Assume there is a valid configuration file
env.setup("config.toml")
env.load(func)
results = env.run(opt=True, force=True)
env.cleanup()
```
"""

import hashlib
import json
import sys
import tempfile
from datetime import datetime
from itertools import product
from pathlib import Path
from typing import Any, Callable, ClassVar, Union

import numpy as np
from joblib import Parallel, cpu_count, delayed
from loguru import logger
from tqdm import tqdm

from yuusim.io.data import save_data
from yuusim.utils.exceptions import ConfigurationError, DataFileNotFoundError
from yuusim.utils.optimize import MemoryReport, OptimizeAnalysis, TimeReport
from yuusim.utils.typing import ArrayLike, ParameterGrid, PathLike, SimulationEnvironmentProtocol

CPU_COUNT = cpu_count() or 1
TEMP_DIR = Path(tempfile.gettempdir())


class SimulationEnvironment(SimulationEnvironmentProtocol):
    """
    A class representing the simulation environment. It manages the initialization,
    configuration loading, simulation execution, and result saving of a simulation project.

    Attributes
    ----------
    BASE_DIRS : ClassVar[list[str]]
        A list of base directories required for the project.
    FIGURE_SUBDIRS : ClassVar[list[str]]
        A list of subdirectories for figures.
    project_name : str
        The name of the project.
    output : Path
        The absolute path of the output directory.
    dirs : dict
        A dictionary containing the paths of various directories in the project.
    timestamp : str
        The timestamp when the simulation starts.
    config : dict
        The configuration information for the simulation.
    param_hash : str
        The hash value of the configuration parameters.
    func : Callable
        The main function of the simulation.
    """

    BASE_DIRS: ClassVar[list[str]] = ["data", "logs", "figures", "tmp", "config", "analysis"]
    FIGURE_SUBDIRS: ClassVar[list[str]] = ["svg", "video", "html"]

    def __init__(self, project_name: str, output: PathLike = ".") -> None:
        """
        Initialize the simulation environment.

        Parameters
        ----------
        project_name : str
            The name of the project.
        output : PathLike, optional
            The output directory. Defaults to the current directory.
        """
        self.project_name = project_name
        self.output = Path(output).absolute()
        self._initialize_folders()

    def __repr__(self) -> str:
        """Return a string representation of the SimulationEnvironment object."""
        return f"SimulationEnvironment(project_name={self.project_name}, save_path={self.dirs['root']})"

    def setup(self, config_path: PathLike, **kwargs: Any) -> None:
        """
        Set up environment parameters from a configuration file.

        Parameters
        ----------
        config_path : PathLike
            The path to the configuration file.
        **kwargs : Any
            Additional keyword arguments for setting up logging.
        """

        self._load_config(config_path)
        self._setup_logging(**kwargs)
        self._log_setup_information(config_path)

    def load(self, func: Callable) -> None:
        """
        Load the main function for the simulation.

        Parameters
        ----------
        func : Callable
            The main function to be used in the simulation.
            It should accept a dictionary of parameters as input and return a result.
            Example: def my_simulation(params: dict) -> Any: ...
        """
        self.func = func
        logger.info(f"Main function loaded: {func.__name__}")
        logger.info(f"Function signature: {func.__code__.co_varnames}")

    def run(self, force: bool = False, opt: bool = True, **kwargs: Any) -> Any:
        """
        Run the main function with provided arguments.

        Parameters
        ----------
        force : bool, optional
            If True, force to run the simulation even if data exists. Defaults to False.
        opt : bool, optional
            If True, analyze the performance of a single run. Defaults to True.
        **kwargs : Any
            Additional keyword arguments for generating parameter sets.

        Returns
        -------
        Any
            The results of the simulation.
        """
        if not force and self._check_existing_data():
            return

        param_sets = self._generate_parameter_sets(**kwargs)
        logger.info(f"Running {len(param_sets)} simulations...")

        if opt:
            self._analyze_single_run_performance(param_sets)

        results = self._execute_simulations(param_sets)
        logger.success("All simulations completed.")

        self._save_results(results)
        return results

    def _log_setup_information(self, config_path: PathLike) -> None:
        """Log information about the setup process."""
        logger.info(f"Initializing simulation environment for project: {self.project_name}")
        logger.info(f"Timestamp for this simulation: {self.timestamp}")
        logger.info(f"Output directory set to: {self.output}")
        logger.info(f"Parameters loaded from {config_path}")
        logger.info(f"Parameter hash: {self.param_hash}")
        logger.info(f"Logging initialized with level: {logger.level}")
        logger.info("Environment setup complete.")

    def _load_config(self, config_path: PathLike) -> None:
        """Load configuration from file and compute parameter hash."""
        from yuusim.io.config import load_config

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            self.config = load_config(config_path)
        except FileNotFoundError as e:
            message = f"Configuration file not found: {config_path}"
            logger.error(message)
            raise DataFileNotFoundError(config_path) from e
        except Exception as e:
            message = f"Error loading configuration file: {e}"
            logger.error(message)
            raise ConfigurationError(message) from e

        config_hash = json.dumps(self.config, sort_keys=True) + self.project_name
        self.param_hash = hashlib.sha256(config_hash.encode()).hexdigest()[:8]

    def _setup_logging(self, **kwargs: Any) -> None:
        """Initialize logging."""
        from yuusim.io.logging import setup_logging

        setup_logging(self, **kwargs)

    def _save_results(self, results: ArrayLike) -> None:
        """Save simulation results and configuration to files."""
        from yuusim.io.config import save_config

        results = np.array(results)
        filename = Path(f"{self.timestamp}_{self.param_hash}")
        save_data(data=results, filename=self.dirs["data"] / filename, metadata=self.config)
        save_config(config=self.config, filename=self.dirs["config"] / filename)

    def _execute_simulations(self, param_sets: list[dict], **kwargs: Any) -> ArrayLike:
        """Execute simulations with batch processing"""
        batch_size = max(1, kwargs.get("batch_size", CPU_COUNT * 100))
        batch_size = min(batch_size, len(param_sets))

        if CPU_COUNT > 1:
            return self._execute_parallel(param_sets, batch_size)
        return self._execute_sequential(param_sets, batch_size)

    def _execute_parallel(self, param_sets: list[dict], batch_size: int) -> ArrayLike:
        """Execute simulations in parallel with batches"""
        logger.info(f"Using {CPU_COUNT} CPU cores for parallel processing (batch size: {batch_size})")
        results = []
        for i in range(0, len(param_sets), batch_size):
            batch = param_sets[i : i + batch_size]
            results.extend(
                list(
                    Parallel(n_jobs=CPU_COUNT)(
                        delayed(self.func)(params) for params in self._create_progress_bar(batch, i // batch_size + 1)
                    )
                )
            )
        return results

    def _execute_sequential(self, param_sets: list[dict], batch_size: int) -> ArrayLike:
        """Execute simulations sequentially with batches"""
        logger.info(f"Using single CPU core (batch size: {batch_size})")
        results: list[Any] = []
        for i in range(0, len(param_sets), batch_size):
            batch = param_sets[i : i + batch_size]
            results.extend(self.func(params) for params in self._create_progress_bar(batch, i // batch_size + 1))
        return results

    def _create_progress_bar(self, param_sets: list[dict], batch_num: int = 1) -> tqdm:
        """Create progress bar for simulation execution"""
        return tqdm(
            param_sets,
            desc=f"Batch {batch_num}",
            unit="simulation",
            leave=False,
            file=sys.stdout,
            ascii=True,
            ncols=100,
        )

    def _analyze_single_run_performance(self, param_sets: list[dict]) -> None:
        """Analyze the performance of a single run."""
        sample_params = param_sets[0]

        mem_report = self._estimate_memory_usage(sample_params)
        self._save_report(mem_report, "memory")

        time_report = self._estimate_time_usage(sample_params)
        self._save_report(time_report, "time")

    def _save_report(self, report: Union[MemoryReport, TimeReport], report_type: str) -> None:
        """Save the memory or time report to a file."""
        log_path = self.dirs["analysis"] / f"{report_type}_{self.timestamp}_{self.param_hash}.log"
        with open(log_path, "w") as f:
            f.write(str(report))

    def _generate_parameter_sets(self, **kwargs: Any) -> list[dict]:
        """Generate parameter sets for each simulation."""
        try:
            param_grid = generate_parameter_grid(self.config["parameters"], kwargs.get("base", 10))
        except KeyError as e:
            logger.warning(f"Missing parameter in configuration: {e}")
            return [self.config["system"]]

        param_sets = []
        system_config = self.config["system"]
        param_names = list(param_grid.keys())
        for values in product(*param_grid.values()):
            param_set = {**system_config}
            for name, value in zip(param_names, values):
                param_set[name] = value
            param_sets.append(param_set)
        return param_sets

    def _check_existing_data(self) -> bool:
        """Check if data with the same parameter hash already exists."""
        data_dir = self.dirs["data"]
        if data_dir.exists():
            for file in data_dir.iterdir():
                if self.param_hash in file.name:
                    warning_msg = f"Data file {file} contains the hash {self.param_hash}. Skipping simulation."
                    logger.warning(warning_msg)
                    return True
        return False

    def cleanup(self, keep_data: bool = True, keep_logs: bool = True) -> None:
        """Clean up temporary files."""
        try:
            self._perform_cleanup_operations(keep_data, keep_logs)
        except FileNotFoundError as e:
            logger.error(f"Directory not found during cleanup: {e}")
            raise
        except PermissionError as e:
            logger.error(f"Permission denied during cleanup: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise

    @staticmethod
    def _cleanup_directory(directory: Path) -> None:
        """Helper method to clean up a directory by removing all files."""
        for item in directory.iterdir():
            if item.is_file():
                item.unlink()

    def _perform_cleanup_operations(self, keep_data: bool, keep_logs: bool) -> None:
        """Perform cleanup operations on temporary files."""
        self._cleanup_directory(self.dirs["tmp"])
        logger.info("Temporary files cleaned up.")

        if not keep_data:
            self._cleanup_directory(self.dirs["data"])

        if not keep_logs:
            self._cleanup_directory(self.dirs["logs"])

        data_files = [file.stem for file in self.dirs["data"].iterdir() if file.suffix == ".h5"]
        self._clean_unused(self.dirs["config"], data_files)
        self._clean_unused(self.dirs["logs"], data_files)

        logger.success("Cleanup completed successfully.")

    def _clean_unused(self, path: Path, data_files: list[str]) -> None:
        """Remove files that are not in the data_files list."""
        for file in path.iterdir():
            if file.stem not in data_files and file.is_file() and self.param_hash not in file.name:
                file.unlink()

    def _initialize_folders(self) -> None:
        """Create necessary directory structure."""
        root = self.output / "simulations" / self.project_name
        try:
            self._create_and_validate_dir_structure(root)
        except PermissionError as e:
            logger.critical(f"Insufficient permissions to create directory: {e}")
            raise
        except FileExistsError as e:
            logger.warning(f"Directory already exists: {e}")
        except OSError as e:
            logger.critical(f"Failed to create directory: {e}")
            raise

    def _create_and_validate_dir_structure(self, root: Path) -> None:
        """Create directory structure and check permissions."""
        # 先检查根目录是否有写权限
        root.mkdir(parents=True, exist_ok=True)
        test_file = root / ".permission_test"
        test_file.touch()
        test_file.unlink()

        self.dirs = {"root": root} | {name: root / name for name in self.BASE_DIRS}
        self.dirs |= {f"figures_{subdir}": self.dirs["figures"] / subdir for subdir in self.FIGURE_SUBDIRS}

        for directory in self.dirs.values():
            directory.mkdir(parents=True, exist_ok=True)

    def _estimate_memory_usage(self, params: dict) -> MemoryReport:
        """Estimate memory usage for a single simulation."""
        analyzer = OptimizeAnalysis(self.func)
        return analyzer.analyze_memory(params)

    def _estimate_time_usage(self, params: dict) -> TimeReport:
        """Estimate time usage for a single simulation."""
        analyzer = OptimizeAnalysis(self.func)
        return analyzer.analyze_time(params)


def generate_parameter_grid(
    parameters: dict[str, dict[str, Any]],
    base: int = 10,
) -> ParameterGrid:
    """
    Generate parameter grid for parameter space exploration.

    Parameters
    ----------
    parameters : dict[str, dict[str, Any]]
        Dictionary of parameter specifications.
        Example: {
            'temperature': {'start': 0.1, 'end': 10.0, 'steps': 100, 'log_scale': True},
            'pressure': {'start': 1.0, 'end': 100.0, 'steps': 50, 'log_scale': False}
        }
    base : int, optional
        Base for logarithmic scaling. Defaults to 10.

    Returns
    -------
    ParameterGrid
        Dictionary of parameter arrays.
    """
    return {
        param: np.logspace(
            np.log10(config["start"]),
            np.log10(config["end"]),
            num=config["steps"],
            base=base,
        )
        if config.get("log_scale", False)
        else np.linspace(
            config["start"],
            config["end"],
            num=config["steps"],
        )
        for param, config in parameters.items()
    }


if __name__ == "__main__":
    env = SimulationEnvironment("test_project")
    # 虚假文件
    import tempfile
    import time

    def func(*args: Any, **kwargs: Any) -> Any:
        time.sleep(1)
        return np.random.rand(10)

    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as tmp:
        tmp.write(b"[system]\nname = 'test'\n")
        tmp.write(b"[parameters]\ntemperature = {start = 0.1, end = 10.0, steps = 100, log_scale = false}")
        tmp_path = Path(tmp.name)
    env.setup(tmp_path)
    env.load(func)
    res = env.run(opt=True, force=True)
    env.cleanup()

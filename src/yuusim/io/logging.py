from typing import Any

from loguru import logger

from yuusim.utils.enums import LogLevel
from yuusim.utils.typing import DictLike, EnvDirs, SimulationEnvironmentProtocol

# Use a more explicit configuration type
LogConfig = DictLike
log_handler_config: LogConfig = {}

DEFAULT_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level.icon}</level> <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# 添加日志级别图标配置
logger.level("TRACE", color="<fg #add8e6>")  # 浅蓝色
logger.level("DEBUG", color="<fg #89cff0>")  # 天蓝色
logger.level("INFO", color="<fg #90EE90>")  # 浅绿色
logger.level("SUCCESS", color="<fg #32CD32>")  # 亮绿色
logger.level("WARNING", color="<fg #FFA500>")  # 橙色
logger.level("ERROR", color="<fg #FF6347>")  # 番茄红
logger.level("CRITICAL", color="<fg #FF0000>")  # 纯红色

# 为每个日志级别添加图标
logger.level("TRACE", icon="🔍")
logger.level("DEBUG", icon="🐛")
logger.level("INFO", icon="[i]")
logger.level("SUCCESS", icon="✅")
logger.level("WARNING", icon="⚠️")
logger.level("ERROR", icon="❌")
logger.level("CRITICAL", icon="💥")


def setup_logging(
    env: SimulationEnvironmentProtocol,
    **kwargs,
) -> None:
    """Initialize and configure the logging system with more customization options.

    Args:
        env: A simulation environment object.
        **kwargs: Additional configuration options:
            - level: Log level (default: INFO).
            - rotation: Log rotation size (default: "1 MB").
            - retention: Number of log files to retain (default: 5).
            - compression: Log compression format (options: "gz", "zip", "tar").
            - log_format: Custom log format string.
            - filename_template: Custom log file name template. Available variables:
                {timestamp}, {project}, {hash}
    """
    level = kwargs.get("level", LogLevel.INFO).value
    rotation = kwargs.get("rotation", "1 MB")
    retention = kwargs.get("retention", 5)
    compression = kwargs.get("compression")
    log_format = kwargs.get("log_format", DEFAULT_FORMAT)
    filename_template = kwargs.get("filename_template")
    dirs: EnvDirs = env.dirs

    # Process the custom file name template
    filename = filename_template or f"{env.timestamp}_{env.param_hash}"
    log_file = dirs["logs"] / f"{filename}.log"

    try:
        global log_handler_config
        log_handler_config = {
            "sink": log_file,
            "level": level,
            "rotation": rotation,
            "retention": retention,
            "compression": compression,
            "format": log_format,
            "enqueue": True,  # Thread-safe
            "backtrace": True,  # Record the full stack
            "diagnose": True,  # Display variable values
        }
        logger.add(**log_handler_config)
        logger.success("Logging system initialized successfully.")
    except Exception as e:
        error_msg = "Logging configuration failed"
        logger.critical(f"{error_msg}: {e}")
        raise RuntimeError(error_msg) from e


def get_logger() -> Any:
    """
    Get the configured logger instance.

    Returns:
        The configured loguru logger instance.
    """
    return logger


def change_log_level(level: LogLevel) -> None:
    """Dynamically change the log level while keeping other configurations."""
    global log_handler_config
    if not log_handler_config:
        logger.warning("The log handler is not initialized. Please call setup_logging first.")
        return

    try:
        logger.remove()
        # Update the log level in the configuration
        log_handler_config["level"] = level.value
        logger.add(**log_handler_config)
        logger.info(f"Log level has been changed to: {level.name}")
    except Exception as e:
        logger.error(f"Failed to change the log level: {e}")
        raise

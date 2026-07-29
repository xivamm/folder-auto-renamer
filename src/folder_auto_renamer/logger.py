"""Centralized logging configuration for folder-auto-renamer."""

import logging
from pathlib import Path
from typing import Optional


def setup_logger(log_file: Path, verbose: bool = False) -> logging.Logger:
    """Configures application logger with file and console handlers.

    Args:
        log_file: Target file path for persistent log file outputs.
        verbose: Enables DEBUG log level if True, otherwise INFO.

    Returns:
        logging.Logger: Configured logger instance for folder-auto-renamer.
    """
    logger = logging.getLogger("folder_auto_renamer")

    # Prevent duplicate handlers if re-initialized
    if logger.handlers:
        return logger

    log_level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(log_level)

    # Ensure log directory exists
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    # File log handler configuration
    try:
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as err:
        # Fallback if file handler creation fails due to permissions
        sys_console = logging.StreamHandler()
        sys_console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(sys_console)
        logger.warning(f"Could not open log file {log_file}: {err}")

    return logger


def get_logger() -> logging.Logger:
    """Retrieves standard logger instance.

    Returns:
        logging.Logger: Named logger instance.
    """
    return logging.getLogger("folder_auto_renamer")


def close_logger_handlers() -> None:
    """Closes and removes all handlers attached to folder_auto_renamer logger."""
    logger = logging.getLogger("folder_auto_renamer")
    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)


"""ANSI terminal coloring utilities with auto-detection for Windows and Unix."""

import os
import sys
import ctypes
from typing import Optional


class TerminalColors:
    """Manages ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RED = "\033[31m"
    CYAN = "\033[36m"

    _enabled: Optional[bool] = None

    @classmethod
    def is_color_supported(cls) -> bool:
        """Determines if the terminal environment supports ANSI escape sequences.

        Returns:
            bool: True if color output is supported and enabled, False otherwise.
        """
        if cls._enabled is not None:
            return cls._enabled

        # Check standard NO_COLOR environment variable convention
        if os.environ.get("NO_COLOR"):
            cls._enabled = False
            return False

        # Disable colors if stdout is redirected to file or pipe
        if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
            cls._enabled = False
            return False

        # Windows Virtual Terminal Processing setup
        if sys.platform == "win32":
            try:
                kernel32 = ctypes.windll.kernel32
                # Enable ENABLE_VIRTUAL_TERMINAL_PROCESSING (0x0004)
                handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                mode = ctypes.c_ulong()
                if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                    kernel32.SetConsoleMode(handle, mode.value | 0x0004)
                    cls._enabled = True
                    return True
            except Exception:
                pass

        # Fallback check for Unix terminals
        term = os.environ.get("TERM", "")
        if term == "dumb":
            cls._enabled = False
            return False

        cls._enabled = True
        return True

    @classmethod
    def set_enabled(cls, enabled: bool) -> None:
        """Manually override color output state.

        Args:
            enabled: True to force colors on, False to disable them.
        """
        cls._enabled = enabled

    @classmethod
    def colorize(cls, text: str, color_code: str) -> str:
        """Wraps text in ANSI color sequence if supported.

        Args:
            text: Input message string.
            color_code: ANSI escape string sequence.

        Returns:
            str: Colorized string or original text if colors disabled.
        """
        if cls.is_color_supported():
            return f"{color_code}{text}{cls.RESET}"
        return text


def green(text: str) -> str:
    """Formats text with green color for success messages."""
    return TerminalColors.colorize(text, TerminalColors.GREEN)


def yellow(text: str) -> str:
    """Formats text with yellow color for warning or skipped messages."""
    return TerminalColors.colorize(text, TerminalColors.YELLOW)


def blue(text: str) -> str:
    """Formats text with blue color for informational messages."""
    return TerminalColors.colorize(text, TerminalColors.BLUE)


def red(text: str) -> str:
    """Formats text with red color for error messages."""
    return TerminalColors.colorize(text, TerminalColors.RED)

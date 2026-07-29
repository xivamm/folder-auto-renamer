"""Helper utilities for filesystem attributes, path checks, and naming calculations."""

import os
import sys
import ctypes
from pathlib import Path


FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_SYSTEM = 0x4


def is_windows_hidden(path: Path) -> bool:
    """Checks whether a file or directory has the Windows hidden attribute set.

    Args:
        path: Path object to inspect.

    Returns:
        bool: True if the file system item is marked hidden on Windows.
    """
    if sys.platform != "win32":
        return False

    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if attrs != -1:
            return bool(attrs & FILE_ATTRIBUTE_HIDDEN)
    except Exception:
        pass

    return False


def is_windows_system(path: Path) -> bool:
    """Checks whether a directory has the Windows system attribute set.

    Args:
        path: Path object to inspect.

    Returns:
        bool: True if the directory is marked as a system directory on Windows.
    """
    if sys.platform != "win32":
        return False

    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        if attrs != -1:
            return bool(attrs & FILE_ATTRIBUTE_SYSTEM)
    except Exception:
        pass

    return False


def is_hidden_folder(path: Path) -> bool:
    """Determines if a directory should be considered hidden or system-restricted.

    Checks for dotfile convention, Windows hidden attribute, and system attribute.

    Args:
        path: Directory path to evaluate.

    Returns:
        bool: True if folder should be ignored as hidden or system directory.
    """
    name = path.name

    # Skip unix-style hidden folders (starting with dot)
    if name.startswith("."):
        return True

    # Check Windows-specific attributes if running on Windows
    if is_windows_hidden(path) or is_windows_system(path):
        return True

    # Common system folder names to protect
    system_folder_names = {
        "$recycle.bin",
        "system volume information",
        "node_modules",
        "__pycache__",
    }

    if name.lower() in system_folder_names:
        return True

    return False


def calculate_zero_padding(start_number: int, total_items: int, min_width: int = 3) -> int:
    """Calculates the minimum zero-padding width required for sequential numbers.

    Ensures digit consistency across all generated folder names.

    Args:
        start_number: Initial number in sequential sequence.
        total_items: Total number of folders being renamed.
        min_width: Minimum default padding width (defaults to 3 digits).

    Returns:
        int: Number of digits to pad sequential integers.
    """
    if total_items <= 0:
        return max(min_width, len(str(start_number)))

    max_number = start_number + total_items - 1
    return max(min_width, len(str(max_number)))


def format_sequential_name(prefix: str, number: int, width: int) -> str:
    """Formats prefix and sequential number with zero-padded formatting.

    Args:
        prefix: Custom string prefix (e.g. 'Project-').
        number: Sequential integer value.
        width: Padding digit width.

    Returns:
        str: Formatted folder name (e.g. 'Project-001').
    """
    formatted_num = str(number).zfill(width)
    return f"{prefix}{formatted_num}"

"""Progress tracker and terminal status formatter for batch processing."""

import sys
from typing import TextIO


class ProgressTracker:
    """Tracks and formats execution progress for folder rename operations."""

    def __init__(self, total: int, stream: TextIO = sys.stdout) -> None:
        """Initializes the progress tracker with item count and stream target.

        Args:
            total: Total number of folders to process.
            stream: File stream target for progress output (defaults to sys.stdout).
        """
        self.total = max(1, total)
        self.current = 0
        self.stream = stream

    def update(self, count: int = 1) -> str:
        """Increments processed items counter and produces formatted progress string.

        Args:
            count: Number of completed items to increment by.

        Returns:
            str: Formatted progress indicator string (e.g. '[1/25] 4%').
        """
        self.current = min(self.total, self.current + count)
        return self.format_status()

    def format_status(self) -> str:
        """Formats current progress into percentage and step ratio format.

        Returns:
            str: Status string formatted as '[current/total] percentage%'.
        """
        percentage = int((self.current / self.total) * 100)
        padding_width = len(str(self.total))
        formatted_current = str(self.current).rjust(padding_width)
        return f"[{formatted_current}/{self.total}] {percentage}%"

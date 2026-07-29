"""Configuration settings and data structures for folder-auto-renamer."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RenamerConfig:
    """Holds operational configuration options for folder auto-renamer.

    Attributes:
        target_path: Path to the target directory containing subfolders to rename.
        prefix: Custom string prefix applied to each folder.
        start: Initial starting number for sequential folder counter.
        dry_run: If True, previews rename actions without modifying disk.
        undo: If True, triggers undo operation using previous history log.
        verbose: If True, outputs detailed debug logging information.
        log_file: Path where log messages are recorded.
        history_file: Path where rename history is saved for undo operations.
    """

    target_path: Optional[Path] = None
    prefix: str = "Project-"
    start: int = 1
    dry_run: bool = False
    undo: bool = False
    verbose: bool = False
    log_file: Path = Path("logs/folder-auto-renamer.log")
    history_file: Path = Path.home() / ".folder_auto_renamer_history.json"

    def validate(self) -> None:
        """Validates configuration settings before starting execution.

        Raises:
            ValueError: If starting number is negative or path validation fails.
        """
        if self.start < 0:
            raise ValueError("Starting number cannot be negative.")

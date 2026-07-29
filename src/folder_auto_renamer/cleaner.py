"""Empty folder scanner and cleaner module."""

import os
from pathlib import Path
from typing import List, Tuple


class EmptyFolderCleaner:
    """Scans and safely removes empty subfolders in target directory."""

    def __init__(self, target_path: Path) -> None:
        """Initializes cleaner with target path."""
        self.target_path = Path(target_path).resolve()

    def scan_empty_folders(self) -> List[Path]:
        """Scans for empty directories recursively (bottom-up)."""
        if not self.target_path.exists() or not self.target_path.is_dir():
            return []

        empty_folders: List[Path] = []

        # Bottom-up walk so child empty folders are identified first
        for root, dirs, files in os.walk(self.target_path, topdown=False):
            root_path = Path(root)
            if root_path == self.target_path:
                continue

            try:
                # Check if directory contains no files and no subdirectories (or only empty ones already scanned)
                remaining_items = list(root_path.iterdir())
                if not remaining_items:
                    empty_folders.append(root_path)
            except Exception:
                continue

        return empty_folders

    def clean(self, dry_run: bool = False) -> Tuple[int, int]:
        """Removes identified empty folders.

        Returns:
            Tuple[int, int]: (removed_count, failed_count)
        """
        empty_folders = self.scan_empty_folders()
        removed_count = 0
        failed_count = 0

        for folder_path in empty_folders:
            if dry_run:
                removed_count += 1
                continue

            try:
                folder_path.rmdir()
                removed_count += 1
            except Exception:
                failed_count += 1

        return (removed_count, failed_count)

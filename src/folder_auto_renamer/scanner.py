"""Directory scanner for discovering and filtering target folders."""

import os
from pathlib import Path
from typing import List

from folder_auto_renamer.exceptions import (
    DirectoryNotFoundError,
    NotADirectoryError,
    PermissionDeniedError,
)
from folder_auto_renamer.utils import is_hidden_folder


class FolderScanner:
    """Scans filesystem directories and identifies valid target folders for renaming."""

    def __init__(self, target_path: Path) -> None:
        """Initializes scanner with target directory path.

        Args:
            target_path: Directory path to scan.
        """
        self.target_path = Path(target_path).resolve()

    def scan(self) -> List[Path]:
        """Scans for valid child directories inside target path.

        Filters out hidden folders, Windows hidden/system attributes, and dotfiles.

        Returns:
            List[Path]: Sorted list of valid child directory paths.

        Raises:
            DirectoryNotFoundError: If target path does not exist.
            NotADirectoryError: If target path exists but is a file.
            PermissionDeniedError: If read permission is denied.
        """
        if not self.target_path.exists():
            raise DirectoryNotFoundError(
                f"Directory does not exist: '{self.target_path}'"
            )

        if not self.target_path.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: '{self.target_path}'"
            )

        valid_folders: List[Path] = []

        try:
            entries = os.scandir(self.target_path)
        except PermissionError as err:
            raise PermissionDeniedError(
                f"Permission denied accessing directory '{self.target_path}': {err}"
            ) from err

        with entries:
            for entry in entries:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        entry_path = Path(entry.path)
                        if not is_hidden_folder(entry_path):
                            valid_folders.append(entry_path)
                except PermissionError:
                    # Skip subdirectories where permission is denied
                    continue

        # Sort folders alphabetically in natural order
        valid_folders.sort(key=lambda p: p.name.lower())
        return valid_folders

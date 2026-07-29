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

    def scan(
        self,
        include_subfolders: bool = False,
        filter_empty_only: bool = False,
        filter_non_empty_only: bool = False,
        sort_order_str: str = "alphabetical",
    ) -> List[Path]:
        """Scans for valid child directories inside target path.

        Args:
            include_subfolders: If True, scans subfolders recursively.
            filter_empty_only: If True, includes only empty directories.
            filter_non_empty_only: If True, includes only non-empty directories.
            sort_order_str: Sorting criteria key.

        Returns:
            List[Path]: Sorted list of valid child directory paths.
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

        if include_subfolders:
            try:
                for root, dirs, _ in os.walk(self.target_path):
                    root_path = Path(root)
                    for d in list(dirs):
                        dir_path = root_path / d
                        if is_hidden_folder(dir_path):
                            dirs.remove(d)
                            continue
                        if self._passes_filter(dir_path, filter_empty_only, filter_non_empty_only):
                            valid_folders.append(dir_path)
            except PermissionError as err:
                raise PermissionDeniedError(
                    f"Permission denied accessing directory '{self.target_path}': {err}"
                ) from err
        else:
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
                                if self._passes_filter(entry_path, filter_empty_only, filter_non_empty_only):
                                    valid_folders.append(entry_path)
                    except PermissionError:
                        continue

        from folder_auto_renamer.utils import sort_folders
        return sort_folders(valid_folders, sort_order_str)

    def _passes_filter(
        self, path: Path, empty_only: bool, non_empty_only: bool
    ) -> bool:
        """Helper to filter empty or non-empty directories."""
        if not empty_only and not non_empty_only:
            return True

        try:
            has_items = any(path.iterdir())
            if empty_only:
                return not has_items
            if non_empty_only:
                return has_items
        except Exception:
            pass

        return True


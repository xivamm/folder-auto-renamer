"""Core folder auto-renaming orchestration engine."""

import os
from pathlib import Path
from typing import Dict, List, Tuple

from folder_auto_renamer.colors import blue, green, red, yellow
from folder_auto_renamer.config import RenamerConfig
from folder_auto_renamer.exceptions import (
    DirectoryNotFoundError,
    PermissionDeniedError,
)
from folder_auto_renamer.logger import get_logger, setup_logger
from folder_auto_renamer.progress import ProgressTracker
from folder_auto_renamer.scanner import FolderScanner
from folder_auto_renamer.undo import UndoManager
from folder_auto_renamer.utils import calculate_zero_padding, format_sequential_name


class FolderRenamer:
    """Executes sequential folder renaming based on configuration rules."""

    def __init__(self, config: RenamerConfig) -> None:
        """Initializes FolderRenamer with operational settings.

        Args:
            config: Validated RenamerConfig object.
        """
        self.config = config
        self.logger = setup_logger(config.log_file, config.verbose)
        self.undo_manager = UndoManager(config.history_file)

    def run(self) -> Tuple[int, int]:
        """Executes the rename process according to configuration parameters.

        Returns:
            Tuple[int, int]: Count of (renamed_folders, skipped_folders).

        Raises:
            DirectoryNotFoundError: If target path is invalid.
            PermissionDeniedError: If permission is denied.
        """
        if self.config.undo:
            self.logger.info("Executing requested undo operation.")
            self.undo_manager.undo_last_session(dry_run=self.config.dry_run)
            return (0, 0)

        if not self.config.target_path:
            raise DirectoryNotFoundError("Target path is required for rename execution.")

        target_dir = self.config.target_path.resolve()
        self.logger.info(f"Starting folder-auto-renamer process in target directory '{target_dir}'")
        self.logger.info(
            f"Parameters: prefix='{self.config.prefix}', start={self.config.start}, dry_run={self.config.dry_run}"
        )

        scanner = FolderScanner(target_dir)
        folders = scanner.scan()

        if not folders:
            msg = f"No eligible folders found to rename in '{target_dir}'"
            self.logger.info(msg)
            print(yellow(msg))
            return (0, 0)

        total_count = len(folders)
        padding_width = calculate_zero_padding(self.config.start, total_count)

        self.logger.info(f"Discovered {total_count} folders. Calculated zero-padding digit width: {padding_width}")
        print(blue(f"Found {total_count} folder(s) to process in '{target_dir}'"))
        if self.config.dry_run:
            print(yellow("=== DRY RUN MODE - No filesystem modifications will be made ===\n"))

        progress = ProgressTracker(total_count)
        history_mappings: List[Dict[str, str]] = []
        renamed_count = 0
        skipped_count = 0

        for idx, folder_path in enumerate(folders):
            current_num = self.config.start + idx
            new_name = format_sequential_name(self.config.prefix, current_num, padding_width)
            old_name = folder_path.name
            target_path = target_dir / new_name

            status = progress.update(1)

            # Skip if folder is already named as expected
            if old_name == new_name:
                msg = f"{status} [SKIPPED] '{old_name}' is already properly named."
                self.logger.info(f"Skipped folder '{old_name}': already named correctly.")
                print(yellow(msg))
                skipped_count += 1
                continue

            # Duplicate protection: skip if target path already exists on disk
            if target_path.exists():
                msg = f"{status} [SKIPPED] Target folder '{new_name}' already exists."
                self.logger.warning(f"Skipped renaming '{old_name}': target '{new_name}' exists.")
                print(yellow(msg))
                skipped_count += 1
                continue

            rename_label = f"{old_name} -> {new_name}"

            if self.config.dry_run:
                msg = f"{status} [DRY-RUN] {rename_label}"
                self.logger.info(f"[DRY-RUN] {rename_label}")
                print(blue(msg))
                renamed_count += 1
            else:
                try:
                    folder_path.rename(target_path)
                    msg = f"{status} [SUCCESS] {rename_label}"
                    self.logger.info(f"Renamed folder: '{old_name}' -> '{new_name}'")
                    print(green(msg))

                    history_mappings.append(
                        {
                            "old_name": old_name,
                            "new_name": new_name,
                            "old_path": str(folder_path.resolve()),
                            "new_path": str(target_path.resolve()),
                        }
                    )
                    renamed_count += 1
                except PermissionError as err:
                    msg = f"{status} [ERROR] Permission denied renaming '{old_name}' to '{new_name}': {err}"
                    self.logger.error(msg)
                    print(red(msg))
                    skipped_count += 1
                except Exception as err:
                    msg = f"{status} [ERROR] Failed to rename '{old_name}' to '{new_name}': {err}"
                    self.logger.error(msg)
                    print(red(msg))
                    skipped_count += 1

        # Record session history for undo functionality if changes occurred
        if not self.config.dry_run and history_mappings:
            self.undo_manager.record_session(history_mappings, target_dir)

        summary = (
            f"\nFinished process. Total: {total_count}, Renamed: {renamed_count}, Skipped: {skipped_count}"
        )
        self.logger.info(summary)
        print(blue(summary))

        return (renamed_count, skipped_count)

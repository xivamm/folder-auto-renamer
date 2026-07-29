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

    def generate_preview(self) -> List[Dict[str, str]]:
        """Generates a preview table of proposed renames without altering disk contents.

        Returns:
            List[Dict[str, str]]: List of records containing 'old_name', 'new_name', 'status', 'old_path', 'new_path', 'conflict'.
        """
        if not self.config.target_path:
            return []

        target_dir = self.config.target_path.resolve()
        scanner = FolderScanner(target_dir)
        folders = scanner.scan(
            include_subfolders=self.config.include_subfolders,
            filter_empty_only=self.config.filter_empty_only,
            filter_non_empty_only=self.config.filter_non_empty_only,
            sort_order_str=self.config.sort_order.value,
        )

        preview_rows: List[Dict[str, str]] = []
        total_count = len(folders)
        from folder_auto_renamer.modes import transform_name

        existing_names_set = {p.name for p in folders}
        generated_target_names: set[str] = set()

        for idx, folder_path in enumerate(folders):
            parent_dir = folder_path.parent
            old_name = folder_path.name
            proposed_name = transform_name(old_name, idx, total_count, self.config)

            status = "Ready"
            conflict = False

            if old_name == proposed_name:
                status = "Unchanged"
            else:
                target_path = parent_dir / proposed_name

                # Auto-indexing resolution if configured
                from folder_auto_renamer.config import DuplicateStrategy
                if self.config.duplicate_strategy == DuplicateStrategy.AUTO_INDEX:
                    counter = 1
                    base_proposed = proposed_name
                    while target_path.exists() or proposed_name in generated_target_names:
                        proposed_name = f"{base_proposed} ({counter})"
                        target_path = parent_dir / proposed_name
                        counter += 1

                elif target_path.exists() and target_path != folder_path:
                    status = "Conflict (Target Exists)"
                    conflict = True

            generated_target_names.add(proposed_name)

            preview_rows.append({
                "old_name": old_name,
                "new_name": proposed_name,
                "status": status,
                "old_path": str(folder_path),
                "new_path": str(parent_dir / proposed_name),
                "conflict": "Yes" if conflict else "No",
            })

        return preview_rows

    def run(self, progress_callback=None) -> Tuple[int, int]:
        """Executes the rename process according to configuration parameters."""
        if self.config.undo:
            self.logger.info("Executing requested undo operation.")
            self.undo_manager.undo_last_session(dry_run=self.config.dry_run)
            return (0, 0)

        if not self.config.target_path:
            raise DirectoryNotFoundError("Target path is required for rename execution.")

        target_dir = self.config.target_path.resolve()
        self.logger.info(f"Starting folder-auto-renamer in directory '{target_dir}'")

        scanner = FolderScanner(target_dir)
        folders = scanner.scan(
            include_subfolders=self.config.include_subfolders,
            filter_empty_only=self.config.filter_empty_only,
            filter_non_empty_only=self.config.filter_non_empty_only,
            sort_order_str=self.config.sort_order.value,
        )

        if not folders:
            msg = f"No eligible folders found to rename in '{target_dir}'"
            self.logger.info(msg)
            print(yellow(msg))
            return (0, 0)

        total_count = len(folders)
        print(blue(f"Found {total_count} folder(s) to process in '{target_dir}'"))
        if self.config.dry_run:
            print(yellow("=== DRY RUN MODE - No filesystem modifications will be made ===\n"))

        progress = ProgressTracker(total_count)
        history_mappings: List[Dict[str, str]] = []
        renamed_count = 0
        skipped_count = 0

        from folder_auto_renamer.modes import transform_name
        from folder_auto_renamer.config import DuplicateStrategy

        generated_target_names: set[str] = set()

        for idx, folder_path in enumerate(folders):
            parent_dir = folder_path.parent
            old_name = folder_path.name
            new_name = transform_name(old_name, idx, total_count, self.config)
            target_path = parent_dir / new_name

            status = progress.update(1)
            if progress_callback:
                progress_callback(idx + 1, total_count)

            if old_name == new_name:
                msg = f"{status} [SKIPPED] '{old_name}' is already properly named."
                self.logger.info(f"Skipped folder '{old_name}': already named correctly.")
                print(yellow(msg))
                skipped_count += 1
                continue

            if target_path.exists():
                if self.config.duplicate_strategy == DuplicateStrategy.AUTO_INDEX:
                    counter = 1
                    base_new = new_name
                    while target_path.exists() or new_name in generated_target_names:
                        new_name = f"{base_new} ({counter})"
                        target_path = parent_dir / new_name
                        counter += 1
                else:
                    msg = f"{status} [SKIPPED] Target folder '{new_name}' already exists."
                    self.logger.warning(f"Skipped renaming '{old_name}': target '{new_name}' exists.")
                    print(yellow(msg))
                    skipped_count += 1
                    continue

            generated_target_names.add(new_name)
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
                except Exception as err:
                    msg = f"{status} [ERROR] Failed to rename '{old_name}' to '{new_name}': {err}"
                    self.logger.error(msg)
                    print(red(msg))
                    skipped_count += 1

        if not self.config.dry_run and history_mappings:
            self.undo_manager.record_session(history_mappings, target_dir)

        summary = (
            f"\nFinished process. Total: {total_count}, Renamed: {renamed_count}, Skipped: {skipped_count}"
        )
        self.logger.info(summary)
        print(blue(summary))

        return (renamed_count, skipped_count)


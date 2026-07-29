"""Undo history management for recording and restoring folder rename sessions."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from folder_auto_renamer.colors import blue, green, red, yellow
from folder_auto_renamer.exceptions import UndoError
from folder_auto_renamer.logger import get_logger


class UndoManager:
    """Manages history persistence and rollback operations for folder renames."""

    def __init__(self, history_file: Path) -> None:
        """Initializes UndoManager with history file destination.

        Args:
            history_file: File path where history JSON is saved.
        """
        self.history_file = Path(history_file)
        self.logger = get_logger()

    def record_session(self, mappings: List[Dict[str, str]], target_dir: Path) -> None:
        """Saves a rename session record to the persistent history file.

        Args:
            mappings: List of dict entries containing 'old_name', 'new_name', 'old_path', 'new_path'.
            target_dir: Target directory where renaming occurred.
        """
        if not mappings:
            return

        session_data = {
            "timestamp": datetime.now().isoformat(),
            "target_dir": str(target_dir.resolve()),
            "count": len(mappings),
            "mappings": mappings,
        }

        history = self._load_all_history()
        history.append(session_data)

        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
            self.logger.debug(f"Saved rename session history to '{self.history_file}'")
        except Exception as err:
            self.logger.error(f"Failed to save undo history file: {err}")

    def _load_all_history(self) -> List[Dict]:
        """Loads complete history list from JSON storage file.

        Returns:
            List[Dict]: List of historical rename sessions.
        """
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception as err:
            self.logger.warning(f"Could not read undo history file: {err}")

        return []

    def get_latest_session(self) -> Optional[Dict]:
        """Retrieves the most recent rename session from history.

        Returns:
            Optional[Dict]: Last recorded session dict or None if history is empty.
        """
        history = self._load_all_history()
        if not history:
            return None
        return history[-1]

    def undo_last_session(self, dry_run: bool = False) -> bool:
        """Restores folder names from the most recent rename operation.

        Args:
            dry_run: If True, previews undo actions without executing file moves.

        Returns:
            bool: True if undo completed successfully.

        Raises:
            UndoError: If no history exists or target folder restoration fails.
        """
        history = self._load_all_history()
        if not history:
            msg = "No undo history available to restore."
            self.logger.warning(msg)
            print(yellow(msg))
            raise UndoError(msg)

        session = history.pop()
        mappings = session.get("mappings", [])
        target_dir = session.get("target_dir", "")
        timestamp = session.get("timestamp", "")

        self.logger.info(f"Starting undo operation for session from {timestamp} in '{target_dir}'")
        print(blue(f"Undoing rename operation from {timestamp}"))
        print(blue(f"Target Directory: {target_dir}\n"))

        restored_count = 0
        skipped_count = 0

        # Process in reverse order to safely reverse sequential modifications
        for item in reversed(mappings):
            current_path = Path(item["new_path"])
            original_path = Path(item["old_path"])
            old_name = item["old_name"]
            new_name = item["new_name"]

            if not current_path.exists():
                msg = f"Skipping restore: Current folder '{new_name}' does not exist at '{current_path}'"
                self.logger.warning(msg)
                print(yellow(msg))
                skipped_count += 1
                continue

            if original_path.exists() and original_path != current_path:
                msg = f"Skipping restore: Original folder name '{old_name}' already exists at destination."
                self.logger.warning(msg)
                print(yellow(msg))
                skipped_count += 1
                continue

            preview_line = f"{new_name} -> {old_name}"
            if dry_run:
                print(green(f"[DRY-RUN UNDO] {preview_line}"))
                self.logger.info(f"[DRY-RUN UNDO] {preview_line}")
                restored_count += 1
            else:
                try:
                    current_path.rename(original_path)
                    print(green(f"[RESTORED] {preview_line}"))
                    self.logger.info(f"Restored: '{new_name}' -> '{old_name}'")
                    restored_count += 1
                except Exception as err:
                    msg = f"Failed to restore '{new_name}' to '{old_name}': {err}"
                    self.logger.error(msg)
                    print(red(msg))
                    skipped_count += 1

        if not dry_run and restored_count > 0:
            # Save updated history (removing the undone session)
            try:
                with open(self.history_file, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=2)
            except Exception as err:
                self.logger.error(f"Failed to update history file after undo: {err}")

        summary = f"Undo operation completed. Restored: {restored_count}, Skipped: {skipped_count}"
        self.logger.info(summary)
        print(blue(f"\n{summary}"))
        return restored_count > 0

    def export_history_to_csv(self, export_path: Path) -> bool:
        """Exports complete rename history to CSV file.

        Args:
            export_path: Destination CSV file path.

        Returns:
            bool: True if export succeeded.
        """
        import csv

        history = self._load_all_history()
        if not history:
            return False

        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Target Directory", "Old Name", "New Name", "Old Path", "New Path"])
                for session in history:
                    timestamp = session.get("timestamp", "")
                    target_dir = session.get("target_dir", "")
                    for item in session.get("mappings", []):
                        writer.writerow([
                            timestamp,
                            target_dir,
                            item.get("old_name", ""),
                            item.get("new_name", ""),
                            item.get("old_path", ""),
                            item.get("new_path", ""),
                        ])
            return True
        except Exception as err:
            self.logger.error(f"Failed to export history to CSV: {err}")
            return False


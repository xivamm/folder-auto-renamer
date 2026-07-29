"""Configuration settings and data structures for folder-auto-renamer."""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional


class RenameMode(Enum):
    """Supported folder renaming modes."""
    SEQUENTIAL = "sequential"
    REPLACE_TEXT = "replace_text"
    ADD_PREFIX = "add_prefix"
    ADD_SUFFIX = "add_suffix"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    TITLE_CASE = "title_case"
    REMOVE_SPACES = "remove_spaces"
    REPLACE_SPACES_UNDERSCORE = "replace_spaces_underscore"
    REMOVE_SPECIAL_CHARS = "remove_special_chars"
    REGEX_REPLACE = "regex_replace"
    INJECT_DATE = "inject_date"


class SortOrder(Enum):
    """Folder sorting modes prior to renaming."""
    ALPHABETICAL = "alphabetical"
    DATE_CREATED = "date_created"
    DATE_MODIFIED = "date_modified"
    FOLDER_SIZE = "folder_size"


class DuplicateStrategy(Enum):
    """Collision resolution strategy for existing target folder names."""
    SKIP = "skip"
    AUTO_INDEX = "auto_index"  # e.g., Folder (1)


@dataclass
class RenamerConfig:
    """Holds operational configuration options for folder auto-renamer."""

    target_path: Optional[Path] = None
    mode: RenameMode = RenameMode.SEQUENTIAL
    prefix: str = "Project-"
    suffix: str = ""
    find_text: str = ""
    replace_text: str = ""
    regex_pattern: str = ""
    regex_replacement: str = ""
    date_format: str = "%Y-%m-%d"  # e.g., 2026-07-29
    date_type: str = "modified"  # 'modified' or 'created'
    filter_pattern: str = ""  # Wildcard/Regex filter for subfolders
    start: int = 1
    min_zero_padding: int = 3
    dry_run: bool = False
    undo: bool = False
    verbose: bool = False
    gui_mode: bool = False

    # Filters and Options
    include_subfolders: bool = False
    skip_hidden: bool = True
    filter_empty_only: bool = False
    filter_non_empty_only: bool = False
    sort_order: SortOrder = SortOrder.ALPHABETICAL
    duplicate_strategy: DuplicateStrategy = DuplicateStrategy.SKIP


    # File paths
    log_file: Path = Path("logs/folder-auto-renamer.log")
    history_file: Path = Path.home() / ".folder_auto_renamer_history.json"
    settings_file: Path = Path.home() / ".folder_auto_renamer_gui_settings.json"

    def validate(self) -> None:
        """Validates configuration settings before starting execution."""
        if self.start < 0:
            raise ValueError("Starting number cannot be negative.")


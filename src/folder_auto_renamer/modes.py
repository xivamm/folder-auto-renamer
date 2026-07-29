"""String transformation engines for various renaming modes."""

import datetime
import re
from pathlib import Path
from typing import Optional
from folder_auto_renamer.config import RenameMode, RenamerConfig
from folder_auto_renamer.utils import format_sequential_name


def transform_name(
    original_name: str,
    index: int,
    total_count: int,
    config: RenamerConfig,
    folder_path: Optional[Path] = None,
) -> str:
    """Transforms an original folder name according to configured rename mode."""
    mode = config.mode

    if mode == RenameMode.SEQUENTIAL:
        from folder_auto_renamer.utils import calculate_zero_padding
        width = calculate_zero_padding(config.start, total_count, config.min_zero_padding)
        current_num = config.start + index
        base_num = str(current_num).zfill(width)
        return f"{config.prefix}{base_num}{config.suffix}"

    elif mode == RenameMode.REPLACE_TEXT:
        if not config.find_text:
            return original_name
        return original_name.replace(config.find_text, config.replace_text)

    elif mode == RenameMode.ADD_PREFIX:
        return f"{config.prefix}{original_name}"

    elif mode == RenameMode.ADD_SUFFIX:
        return f"{original_name}{config.suffix}"

    elif mode == RenameMode.UPPERCASE:
        return original_name.upper()

    elif mode == RenameMode.LOWERCASE:
        return original_name.lower()

    elif mode == RenameMode.TITLE_CASE:
        return original_name.title()

    elif mode == RenameMode.REMOVE_SPACES:
        return original_name.replace(" ", "")

    elif mode == RenameMode.REPLACE_SPACES_UNDERSCORE:
        return original_name.replace(" ", "_")

    elif mode == RenameMode.REMOVE_SPECIAL_CHARS:
        # Removes all non-alphanumeric characters except spaces, dashes, and underscores
        cleaned = re.sub(r"[^\w\s-]", "", original_name)
        return cleaned.strip()

    elif mode == RenameMode.REGEX_REPLACE:
        if not config.regex_pattern:
            return original_name
        try:
            return re.sub(config.regex_pattern, config.regex_replacement, original_name)
        except re.error:
            return original_name

    elif mode == RenameMode.INJECT_DATE:
        dt = datetime.datetime.now()
        if folder_path and folder_path.exists():
            try:
                stat = folder_path.stat()
                timestamp = stat.st_ctime if config.date_type == "created" else stat.st_mtime
                dt = datetime.datetime.fromtimestamp(timestamp)
            except Exception:
                pass
        date_str = dt.strftime(config.date_format or "%Y-%m-%d")
        if config.prefix:
            return f"{date_str}_{original_name}"
        return f"{date_str}_{original_name}"

    return original_name


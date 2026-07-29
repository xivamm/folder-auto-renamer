"""File organizer engine categorizing and decluttering files into subfolders."""

import datetime
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Mapping of standard file categories to extension lists
CATEGORY_MAP: Dict[str, List[str]] = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico", ".tiff", ".raw"],
    "Documents": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt", ".csv", ".epub", ".rtf"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".iso"],
    "Code & Data": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".sql", ".sh", ".bat", ".md"],
    "Executables & Installers": [".exe", ".msi", ".apk", ".dmg", ".deb", ".rpm"],
}


class FileOrganizer:
    """Organizes files inside a target directory based on category, extension, or date."""

    def __init__(self, target_path: Path) -> None:
        """Initializes organizer with target path."""
        self.target_path = Path(target_path).resolve()

    def get_category_for_file(self, file_path: Path) -> str:
        """Determines category folder name for a given file extension."""
        ext = file_path.suffix.lower()
        if not ext:
            return "Others"

        for category, extensions in CATEGORY_MAP.items():
            if ext in extensions:
                return category

        return f"Files_{ext[1:].upper()}"

    def generate_organize_preview(
        self, mode: str = "category", include_subfolders: bool = False
    ) -> List[Dict[str, str]]:
        """Generates a preview of file movements without modifying disk contents.

        Args:
            mode: 'category' (Images, Documents, etc.), 'extension' (PNG, PDF, etc.), or 'date' (YYYY-MM).
            include_subfolders: Whether to scan subdirectories for files.

        Returns:
            List of dictionaries with 'file_name', 'current_path', 'proposed_folder', 'proposed_path', 'status'.
        """
        if not self.target_path.exists() or not self.target_path.is_dir():
            return []

        preview_rows: List[Dict[str, str]] = []
        files_to_process: List[Path] = []

        if include_subfolders:
            for root, _, files in os.walk(self.target_path):
                root_path = Path(root)
                for f in files:
                    file_path = root_path / f
                    files_to_process.append(file_path)
        else:
            for item in self.target_path.iterdir():
                if item.is_file():
                    files_to_process.append(item)

        for file_path in files_to_process:
            file_name = file_path.name
            target_subfolder = "Others"

            if mode == "extension":
                ext = file_path.suffix.lower().lstrip(".")
                target_subfolder = ext.upper() if ext else "No_Extension"
            elif mode == "date":
                try:
                    mtime = file_path.stat().st_mtime
                    dt = datetime.datetime.fromtimestamp(mtime)
                    target_subfolder = dt.strftime("%Y/%Y-%m")
                except Exception:
                    target_subfolder = "Unknown_Date"
            else:  # category
                target_subfolder = self.get_category_for_file(file_path)

            proposed_dir = self.target_path / target_subfolder
            proposed_path = proposed_dir / file_name

            status = "Ready to Move"
            if file_path.parent == proposed_dir:
                status = "Already Organized"

            preview_rows.append({
                "file_name": file_name,
                "current_path": str(file_path),
                "proposed_folder": target_subfolder,
                "proposed_path": str(proposed_path),
                "status": status,
            })

        return preview_rows

    def organize(
        self, mode: str = "category", include_subfolders: bool = False, dry_run: bool = False
    ) -> Tuple[int, int]:
        """Executes file organization into subfolders."""
        preview_rows = self.generate_organize_preview(mode=mode, include_subfolders=include_subfolders)
        moved_count = 0
        skipped_count = 0

        for row in preview_rows:
            if row["status"] == "Already Organized":
                skipped_count += 1
                continue

            current_p = Path(row["current_path"])
            proposed_p = Path(row["proposed_path"])

            if dry_run:
                moved_count += 1
                continue

            try:
                proposed_p.parent.mkdir(parents=True, exist_ok=True)
                # Auto-indexing if destination exists
                target_dest = proposed_p
                counter = 1
                while target_dest.exists() and target_dest != current_p:
                    stem = proposed_p.stem
                    suffix = proposed_p.suffix
                    target_dest = proposed_p.parent / f"{stem} ({counter}){suffix}"
                    counter += 1

                shutil.move(str(current_p), str(target_dest))
                moved_count += 1
            except Exception:
                skipped_count += 1

        return (moved_count, skipped_count)

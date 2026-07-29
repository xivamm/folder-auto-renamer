"""Folder Auto Renamer package."""

__version__ = "1.0.0"
__author__ = "xivamm"
__license__ = "MIT"

from folder_auto_renamer.config import RenamerConfig
from folder_auto_renamer.renamer import FolderRenamer
from folder_auto_renamer.scanner import FolderScanner
from folder_auto_renamer.undo import UndoManager

__all__ = [
    "FolderRenamer",
    "FolderScanner",
    "UndoManager",
    "RenamerConfig",
]

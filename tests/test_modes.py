"""Unit tests for renaming modes and string transformations."""

import sys
import unittest
from pathlib import Path

# Add src to PYTHONPATH
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from folder_auto_renamer.config import RenameMode, RenamerConfig
from folder_auto_renamer.modes import transform_name


class TestRenameModes(unittest.TestCase):
    """Test suite covering string transformation rules across all 10 modes."""

    def test_sequential_mode(self) -> None:
        """Verifies sequential numbering with zero-padding."""
        config = RenamerConfig(mode=RenameMode.SEQUENTIAL, prefix="Project-", start=1, min_zero_padding=3)
        self.assertEqual(transform_name("Photos", 0, 5, config), "Project-001")
        self.assertEqual(transform_name("Images", 1, 5, config), "Project-002")

    def test_replace_text_mode(self) -> None:
        """Verifies text replacement mode."""
        config = RenamerConfig(mode=RenameMode.REPLACE_TEXT, find_text="Vacation", replace_text="Trip")
        self.assertEqual(transform_name("Summer Vacation 2026", 0, 1, config), "Summer Trip 2026")

    def test_add_prefix_mode(self) -> None:
        """Verifies prefix prepending mode."""
        config = RenamerConfig(mode=RenameMode.ADD_PREFIX, prefix="2026_")
        self.assertEqual(transform_name("Photos", 0, 1, config), "2026_Photos")

    def test_add_suffix_mode(self) -> None:
        """Verifies suffix appending mode."""
        config = RenamerConfig(mode=RenameMode.ADD_SUFFIX, suffix="_Backup")
        self.assertEqual(transform_name("Documents", 0, 1, config), "Documents_Backup")

    def test_casing_modes(self) -> None:
        """Verifies uppercase, lowercase, and title case transformations."""
        cfg_upper = RenamerConfig(mode=RenameMode.UPPERCASE)
        self.assertEqual(transform_name("my project folder", 0, 1, cfg_upper), "MY PROJECT FOLDER")

        cfg_lower = RenamerConfig(mode=RenameMode.LOWERCASE)
        self.assertEqual(transform_name("My Project Folder", 0, 1, cfg_lower), "my project folder")

        cfg_title = RenamerConfig(mode=RenameMode.TITLE_CASE)
        self.assertEqual(transform_name("my project folder", 0, 1, cfg_title), "My Project Folder")

    def test_space_cleaning_modes(self) -> None:
        """Verifies space removal and space-to-underscore replacement."""
        cfg_rem = RenamerConfig(mode=RenameMode.REMOVE_SPACES)
        self.assertEqual(transform_name("Client Folder Name", 0, 1, cfg_rem), "ClientFolderName")

        cfg_und = RenamerConfig(mode=RenameMode.REPLACE_SPACES_UNDERSCORE)
        self.assertEqual(transform_name("Client Folder Name", 0, 1, cfg_und), "Client_Folder_Name")

    def test_remove_special_characters(self) -> None:
        """Verifies removal of special characters from folder names."""
        cfg_spec = RenamerConfig(mode=RenameMode.REMOVE_SPECIAL_CHARS)
        self.assertEqual(transform_name("Project #1! (Draft & Final)", 0, 1, cfg_spec), "Project 1 Draft  Final")


if __name__ == "__main__":
    unittest.main()

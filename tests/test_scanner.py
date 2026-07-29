"""Unit tests for directory scanning and filtering."""

import sys
import tempfile
import unittest
from pathlib import Path

# Add src to PYTHONPATH
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from folder_auto_renamer.exceptions import (
    DirectoryNotFoundError,
    NotADirectoryError,
)
from folder_auto_renamer.scanner import FolderScanner
from folder_auto_renamer.utils import calculate_zero_padding, is_hidden_folder



class TestFolderScanner(unittest.TestCase):
    """Test suite covering directory scanner functionality."""

    def setUp(self) -> None:
        """Sets up temporary test directory environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        """Cleans up temporary directory after test execution."""
        self.temp_dir.cleanup()

    def test_scan_regular_folders(self) -> None:
        """Verifies scanning discovers normal visible subdirectories."""
        (self.base_path / "Photos").mkdir()
        (self.base_path / "Documents").mkdir()
        (self.base_path / "Downloads").mkdir()
        # Create a file to ensure files are not treated as directories
        (self.base_path / "notes.txt").write_text("sample content")

        scanner = FolderScanner(self.base_path)
        folders = scanner.scan()

        folder_names = [f.name for f in folders]
        self.assertEqual(len(folder_names), 3)
        self.assertIn("Photos", folder_names)
        self.assertIn("Documents", folder_names)
        self.assertIn("Downloads", folder_names)

    def test_ignore_hidden_dot_folders(self) -> None:
        """Verifies folders starting with dot are excluded from scan."""
        (self.base_path / "VisibleFolder").mkdir()
        (self.base_path / ".git").mkdir()
        (self.base_path / ".cache").mkdir()

        scanner = FolderScanner(self.base_path)
        folders = scanner.scan()

        folder_names = [f.name for f in folders]
        self.assertEqual(len(folder_names), 1)
        self.assertEqual(folder_names[0], "VisibleFolder")

    def test_invalid_directory_path(self) -> None:
        """Verifies DirectoryNotFoundError is raised for non-existent paths."""
        invalid_path = self.base_path / "non_existent_folder"
        scanner = FolderScanner(invalid_path)

        with self.assertRaises(DirectoryNotFoundError):
            scanner.scan()

    def test_file_instead_of_directory(self) -> None:
        """Verifies NotADirectoryError is raised when target path is a file."""
        file_path = self.base_path / "file.txt"
        file_path.write_text("data")

        scanner = FolderScanner(file_path)
        with self.assertRaises(NotADirectoryError):
            scanner.scan()

    def test_zero_padding_calculation(self) -> None:
        """Verifies digit padding calculations for sequential numbers."""
        # 4 items starting from 1 -> 3 digit minimum width: 001, 002, 003, 004
        self.assertEqual(calculate_zero_padding(1, 4), 3)

        # Starting from 1000 with 5 items -> max num is 1004 (4 digits)
        self.assertEqual(calculate_zero_padding(1000, 5), 4)

        # Starting from 99 with 5 items -> max num is 103 (3 digits)
        self.assertEqual(calculate_zero_padding(99, 5), 3)


if __name__ == "__main__":
    unittest.main()

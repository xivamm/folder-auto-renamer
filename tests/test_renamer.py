"""Unit tests for core sequential renaming operations and rules."""

import sys
import tempfile
import unittest
from pathlib import Path

# Add src to PYTHONPATH
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from folder_auto_renamer.config import RenamerConfig
from folder_auto_renamer.renamer import FolderRenamer



class TestFolderRenamer(unittest.TestCase):
    """Test suite covering folder renaming logic."""

    def setUp(self) -> None:
        """Initializes temporary test directory structure."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.log_file = self.base_path / "test.log"
        self.history_file = self.base_path / "test_history.json"

    def tearDown(self) -> None:
        """Cleans up temporary directory resources."""
        from folder_auto_renamer.logger import close_logger_handlers
        close_logger_handlers()
        self.temp_dir.cleanup()

    def test_sequential_rename_default(self) -> None:
        """Verifies standard sequential folder renaming with default prefix."""
        (self.base_path / "Photos").mkdir()
        (self.base_path / "Images").mkdir()
        (self.base_path / "Backup").mkdir()

        config = RenamerConfig(
            target_path=self.base_path,
            prefix="Project-",
            start=1,
            log_file=self.log_file,
            history_file=self.history_file,
        )

        renamer = FolderRenamer(config)
        renamed, skipped = renamer.run()

        self.assertEqual(renamed, 3)
        self.assertEqual(skipped, 0)
        self.assertTrue((self.base_path / "Project-001").exists())
        self.assertTrue((self.base_path / "Project-002").exists())
        self.assertTrue((self.base_path / "Project-003").exists())

    def test_custom_prefix_and_start_number(self) -> None:
        """Verifies custom prefix and starting counter configuration."""
        (self.base_path / "Alpha").mkdir()
        (self.base_path / "Beta").mkdir()

        config = RenamerConfig(
            target_path=self.base_path,
            prefix="Client-",
            start=101,
            log_file=self.log_file,
            history_file=self.history_file,
        )

        renamer = FolderRenamer(config)
        renamed, skipped = renamer.run()

        self.assertEqual(renamed, 2)
        self.assertTrue((self.base_path / "Client-101").exists())
        self.assertTrue((self.base_path / "Client-102").exists())

    def test_dry_run_mode(self) -> None:
        """Verifies dry-run previews renames without altering disk contents."""
        (self.base_path / "FolderA").mkdir()
        (self.base_path / "FolderB").mkdir()

        config = RenamerConfig(
            target_path=self.base_path,
            prefix="IMG-",
            start=1,
            dry_run=True,
            log_file=self.log_file,
            history_file=self.history_file,
        )

        renamer = FolderRenamer(config)
        renamed, skipped = renamer.run()

        self.assertEqual(renamed, 2)
        self.assertEqual(skipped, 0)
        # Original folder names must remain unchanged
        self.assertTrue((self.base_path / "FolderA").exists())
        self.assertTrue((self.base_path / "FolderB").exists())
        self.assertFalse((self.base_path / "IMG-001").exists())

    def test_duplicate_folder_protection(self) -> None:
        """Verifies target collision detection skips existing folders."""
        (self.base_path / "Docs").mkdir()
        (self.base_path / "Project-001").mkdir()  # Target name collision

        config = RenamerConfig(
            target_path=self.base_path,
            prefix="Project-",
            start=1,
            log_file=self.log_file,
            history_file=self.history_file,
        )

        renamer = FolderRenamer(config)
        renamed, skipped = renamer.run()

        # Docs -> Project-001 collides, so it is skipped (Docs remains).
        # Project-001 -> Project-002 is executed.
        self.assertEqual(skipped, 1)
        self.assertTrue((self.base_path / "Docs").exists())
        self.assertTrue((self.base_path / "Project-002").exists())



if __name__ == "__main__":
    unittest.main()

"""Unit tests for undo functionality and rename history persistence."""

import sys
import tempfile
import unittest
from pathlib import Path

# Add src to PYTHONPATH
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from folder_auto_renamer.config import RenamerConfig
from folder_auto_renamer.exceptions import UndoError
from folder_auto_renamer.renamer import FolderRenamer
from folder_auto_renamer.undo import UndoManager



class TestUndoManager(unittest.TestCase):
    """Test suite covering undo operations and history management."""

    def setUp(self) -> None:
        """Sets up temporary test workspace and history destination."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.log_file = self.base_path / "test.log"
        self.history_file = self.base_path / "undo_history.json"

    def tearDown(self) -> None:
        """Cleans up temporary directory resources."""
        from folder_auto_renamer.logger import close_logger_handlers
        close_logger_handlers()
        self.temp_dir.cleanup()


    def test_undo_restores_original_folder_names(self) -> None:
        """Verifies undo restores folder names to their exact initial state."""
        (self.base_path / "Photos").mkdir()
        (self.base_path / "Images").mkdir()

        config = RenamerConfig(
            target_path=self.base_path,
            prefix="Project-",
            start=1,
            log_file=self.log_file,
            history_file=self.history_file,
        )

        renamer = FolderRenamer(config)
        renamer.run()

        self.assertTrue((self.base_path / "Project-001").exists())
        self.assertTrue((self.base_path / "Project-002").exists())

        # Perform undo
        undo_config = RenamerConfig(
            target_path=self.base_path,
            undo=True,
            log_file=self.log_file,
            history_file=self.history_file,
        )

        undo_renamer = FolderRenamer(undo_config)
        undo_renamer.run()

        # Original folder names must be restored
        self.assertTrue((self.base_path / "Photos").exists())
        self.assertTrue((self.base_path / "Images").exists())
        self.assertFalse((self.base_path / "Project-001").exists())
        self.assertFalse((self.base_path / "Project-002").exists())

    def test_undo_with_no_history_raises_error(self) -> None:
        """Verifies UndoError is raised when attempting undo with no history file."""
        undo_manager = UndoManager(self.history_file)
        with self.assertRaises(UndoError):
            undo_manager.undo_last_session()


if __name__ == "__main__":
    unittest.main()

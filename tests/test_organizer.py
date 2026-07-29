"""Unit tests for FileOrganizer and EmptyFolderCleaner."""

import shutil
import tempfile
import unittest
from pathlib import Path
from folder_auto_renamer.cleaner import EmptyFolderCleaner
from folder_auto_renamer.organizer import FileOrganizer


class TestFileOrganizerAndCleaner(unittest.TestCase):
    """Test suite for FileOrganizer and EmptyFolderCleaner."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_organize_by_category(self):
        (self.temp_dir / "photo.png").write_text("dummy image")
        (self.temp_dir / "document.pdf").write_text("dummy doc")
        (self.temp_dir / "script.py").write_text("print(1)")

        organizer = FileOrganizer(self.temp_dir)
        moved, skipped = organizer.organize(mode="category")

        self.assertEqual(moved, 3)
        self.assertTrue((self.temp_dir / "Images" / "photo.png").exists())
        self.assertTrue((self.temp_dir / "Documents" / "document.pdf").exists())
        self.assertTrue((self.temp_dir / "Code & Data" / "script.py").exists())

    def test_organize_by_extension(self):
        (self.temp_dir / "image.jpg").write_text("dummy")
        (self.temp_dir / "archive.zip").write_text("dummy")

        organizer = FileOrganizer(self.temp_dir)
        moved, skipped = organizer.organize(mode="extension")

        self.assertEqual(moved, 2)
        self.assertTrue((self.temp_dir / "JPG" / "image.jpg").exists())
        self.assertTrue((self.temp_dir / "ZIP" / "archive.zip").exists())

    def test_clean_empty_folders(self):
        empty1 = self.temp_dir / "EmptySub1"
        empty2 = self.temp_dir / "EmptySub2" / "ChildEmpty"
        not_empty = self.temp_dir / "ActiveFolder"

        empty1.mkdir()
        empty2.mkdir(parents=True)
        not_empty.mkdir()
        (not_empty / "file.txt").write_text("data")

        cleaner = EmptyFolderCleaner(self.temp_dir)
        removed, failed = cleaner.clean()

        self.assertGreaterEqual(removed, 2)
        self.assertFalse(empty1.exists())
        self.assertTrue(not_empty.exists())


if __name__ == "__main__":
    unittest.main()

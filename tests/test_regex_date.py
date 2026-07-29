"""Unit tests for Regex Replace, Date Injection, and Pattern Filtering."""

import unittest
from pathlib import Path
from folder_auto_renamer.config import RenameMode, RenamerConfig
from folder_auto_renamer.modes import transform_name
from folder_auto_renamer.scanner import FolderScanner


class TestRegexAndDateModes(unittest.TestCase):
    """Test suite for v1.2.0 Regex Replace and Date Injection modes."""

    def test_regex_replace_remove_leading_numbers(self):
        config = RenamerConfig(
            mode=RenameMode.REGEX_REPLACE,
            regex_pattern=r"^\d+[-_\s]*",
            regex_replacement="",
        )
        res = transform_name("01_ProjectAlpha", 0, 1, config)
        self.assertEqual(res, "ProjectAlpha")

    def test_regex_replace_capture_groups(self):
        config = RenamerConfig(
            mode=RenameMode.REGEX_REPLACE,
            regex_pattern=r"^(\d{4})-(\d{2})",
            regex_replacement=r"\2_\1",
        )
        res = transform_name("2026-07-Report", 0, 1, config)
        self.assertEqual(res, "07_2026-Report")

    def test_inject_date_mode(self):
        config = RenamerConfig(
            mode=RenameMode.INJECT_DATE,
            date_format="%Y-%m",
        )
        res = transform_name("FolderA", 0, 1, config)
        self.assertTrue("FolderA" in res)
        self.assertTrue("-" in res)

    def test_scanner_pattern_filtering(self):
        import tempfile, shutil
        temp_dir = Path(tempfile.mkdtemp())
        try:
            (temp_dir / "Backup_2026").mkdir()
            (temp_dir / "Project_Alpha").mkdir()
            (temp_dir / "Backup_2025").mkdir()

            scanner = FolderScanner(temp_dir)
            results = scanner.scan(filter_pattern="Backup_*")
            names = [p.name for p in results]
            self.assertIn("Backup_2026", names)
            self.assertIn("Backup_2025", names)
            self.assertNotIn("Project_Alpha", names)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

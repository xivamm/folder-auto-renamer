"""Test suite package for folder-auto-renamer."""

import sys
from pathlib import Path

# Add src directory to python search path for running tests directly
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


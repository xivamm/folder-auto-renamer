# Auto Folder Renamer Pro

[![Build Status](https://github.com/xivamm/folder-auto-renamer/actions/workflows/ci.yml/badge.svg)](https://github.com/xivamm/folder-auto-renamer/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0%20external-brightgreen.svg)](README.md)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](README.md)

> Rename hundreds of folders in seconds — no coding required. Standalone One-Click Executable & Open-Source Python Utility.

`Auto Folder Renamer Pro` is a professional desktop application and Windows command-line utility built entirely with Python 3.11+ and standard library (`tkinter`, `ttk`). It automatically scans subdirectories and renames them using customizable modes (including Regex Search/Replace and Creation/Modification Date Stamps), live previewing, zero-padding, collision safety checks, dark mode support, presets, and persistent undo history.

---

## 🚀 Key Features

- **Desktop GUI & CLI Dual Execution**: Run as a graphical Tkinter desktop app (`folder-auto-renamer --gui`) or headlessly via command-line interface.
- **🧹 Smart File & Folder Declutter Engine (NEW in v2.0.0)**:
  - **Auto-Organize Files by Category**: Automatically sort files into `Images`, `Documents`, `Videos`, `Audio`, `Archives`, `Code & Data`, `Executables & Installers`.
  - **Auto-Organize Files by Extension**: Group files into folders named by file extension (`.PNG`, `.PDF`, `.MP4`, etc.).
  - **Auto-Organize Files by Date**: Organize files into Year/Month folder structures (`2026/07-July/`).
  - **1-Click "Clean Downloads / Desktop" Presets**: Instant declutter button for chaotic `Downloads` or `Desktop` folders.
  - **Empty Subfolder Cleaner**: 1-click tool to safely identify and delete empty folders.
- **12 Advanced Folder Renaming Modes**:
  1. **Sequential**: `Project-001`, `Project-002`
  2. **Replace Text**: Swap specific text substrings (e.g. `Vacation -> Trip`)
  3. **Regex Search & Replace**: Capture groups and pattern matching (e.g. `^(\d{4})-(\d{2})` -> `\2_\1`)
  4. **Date Stamp Injection**: Prepend/append folder Creation or Modification Dates (e.g. `2026-07-29_MyFolder`)
  5. **Add Prefix**: Prepend custom string (e.g. `2026_`)
  6. **Add Suffix**: Append custom string (e.g. `_Backup`)
  7. **Uppercase**: `MY_FOLDER`
  8. **Lowercase**: `my_folder`
  9. **Title Case**: `My Folder Name`
  10. **Remove Spaces**: `MyFolderName`
  11. **Replace Spaces with Underscore**: `My_Folder_Name`
  12. **Clean Special Characters**: Remove non-alphanumeric special characters.
- **Windows Explorer Right-Click Integration**: 1-click button to register "Open in Auto Folder Renamer Pro" directly into Windows File Explorer's right-click context menu.
- **Regex Preset Templates**: Built-in 1-click templates for quick Regex operations (Remove Numbers, Format Dates, Sanitize Slugs).
- **Live Preview Table**: Interactive `Treeview` displaying current folder name vs proposed new name, with color-coded collision indicators.
- **One-Click Naming & Declutter Presets**: Quick-apply preset configurations for Camera Photos (`IMG-`), YouTube Projects (`Video-`), School Files (`Class-`), Client Projects (`Client-`), Clean Downloads, and Clean Desktop.
- **Dark & Light Mode Support**: Instant theme toggle for comfortable viewing.
- **Auto-Indexing Duplicate Protection**: Resolve existing folder collisions automatically with index suffixes (e.g. `Project (1)`).
- **Sorting & Pattern Filtering**: Sort folders by Name, Date Created, Date Modified, or Folder Size. Filter target subfolders using wildcards (`*2026*`).
- **CSV History Export**: Export undo history logs to CSV spreadsheet files.
- **Persistent Settings**: Saves last-used directory and UI preferences to `~/.folder_auto_renamer_gui_settings.json`.
- **Zero Third-Party Dependencies**: Pure Python Standard Library implementation (`tkinter`, `ttk`, `re`, `datetime`, `shutil`, `json`, `csv`, `pathlib`).




---

## Installation

### From Source

Clone the repository and install locally:

```bash
git clone https://github.com/xivamm/folder-auto-renamer.git
cd folder-auto-renamer
pip install -e .
```

Alternatively, run directly as a module without installation:

```bash
python -m src.folder_auto_renamer D:\Pictures
```

---

## Quick Start

Basic usage renaming all subdirectories in `D:\Pictures`:

```bash
folder-auto-renamer D:\Pictures
```

Output:

```text
Found 4 folder(s) to process in 'D:\Pictures'
[1/4] 25% [SUCCESS] Photos -> Project-001
[2/4] 50% [SUCCESS] Images -> Project-002
[3/4] 75% [SUCCESS] Backup -> Project-003
[4/4] 100% [SUCCESS] Projects -> Project-004

Finished process. Total: 4, Renamed: 4, Skipped: 0
```

---

## CLI Examples

### Custom Prefix

```bash
folder-auto-renamer D:\Pictures --prefix IMG-
```

Transformations:
- `Holiday -> IMG-001`
- `Vacation -> IMG-002`

### Custom Starting Number

```bash
folder-auto-renamer D:\Pictures --prefix Client- --start 101
```

Transformations:
- `Alpha -> Client-101`
- `Beta -> Client-102`

### Dry-Run Preview Mode

```bash
folder-auto-renamer D:\Pictures --dry-run
```

Outputs preview without renaming any folders.

### Undo Last Rename Session

```bash
folder-auto-renamer --undo
```

Restores exact original folder names from history log.

---

## Screenshots Section

```text
+-----------------------------------------------------------------------+
| > folder-auto-renamer D:\Projects --prefix Client- --start 100        |
|                                                                       |
| Found 3 folder(s) to process in 'D:\Projects'                         |
| [1/3] 33% [SUCCESS] Alpha -> Client-100                               |
| [2/3] 66% [SUCCESS] Beta  -> Client-101                               |
| [3/3] 100% [SUCCESS] Gamma -> Client-102                              |
|                                                                       |
| Finished process. Total: 3, Renamed: 3, Skipped: 0                    |
+-----------------------------------------------------------------------+
```

---

## Architecture Overview

`folder-auto-renamer` follows a modular software architecture:

- **CLI Layer (`cli.py`)**: Handles CLI arguments via `argparse` and validates configurations.
- **Scanner Engine (`scanner.py`)**: Performs filesystem discovery and filters hidden folders.
- **Renamer Engine (`renamer.py`)**: Manages zero-padding calculations, collision checks, and file system renames.
- **Undo Engine (`undo.py`)**: Manages JSON state persistence in `~/.folder_auto_renamer_history.json`.
- **System Utilities (`utils.py`)**: Interfaces with Windows Win32 API (`ctypes.windll.kernel32`) for file attributes.
- **Terminal System (`colors.py` & `progress.py`)**: Manages ANSI terminal escape codes and percentage progress strings.

For detailed design specifications, see [docs/architecture.md](docs/architecture.md).

---

## Undo Explanation

Every successful rename session records a JSON payload containing original and new folder paths to `~/.folder_auto_renamer_history.json`.

When `--undo` is invoked:
1. The history manager retrieves the latest session.
2. It processes target paths in reverse order.
3. Original folder names are restored safely while checking for destination collisions.
4. History data persists across terminal and system restarts.

---

## Logging Explanation

Logging is configured through standard Python `logging`.

Log messages are recorded to:
```text
logs/folder-auto-renamer.log
```

Log contents include:
- Execution timestamps and CLI parameters.
- Renamed and skipped folders with details.
- Warning logs for target collisions.
- Full error stack traces when exceptions occur.

---

## Development Guide

### Environment Setup

```bash
git clone https://github.com/xivamm/folder-auto-renamer.git
cd folder-auto-renamer
python -m venv venv
venv\Scripts\activate
```

### Running Tests

Execute the complete unittest suite:

```bash
python -m unittest discover -s tests -v
```

---

## Contribution Guide

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting issues and pull requests.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## FAQ

#### Q: Does folder-auto-renamer work on Linux and macOS?
Yes. While optimized for Windows hidden folder detection via Win32 attributes, it runs seamlessly on Unix-like operating systems.

#### Q: What happens if a destination folder already exists?
`folder-auto-renamer` features duplicate protection. If a target folder name already exists, the application skips it, logs a warning, and continues processing remaining folders.

#### Q: Are external pip packages required?
No. `folder-auto-renamer` requires zero third-party dependencies and uses Python 3.11+ standard library exclusively.

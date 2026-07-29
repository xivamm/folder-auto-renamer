# folder-auto-renamer

> Automatically rename folders with intelligent sequential naming.

`folder-auto-renamer` is a professional, high-performance Windows command-line utility built entirely with the Python Standard Library. It automatically scans subdirectories inside a target directory and renames them sequentially according to customizable rules, zero-padding standards, and collision safety checks.

---

## Features

- **Sequential Renaming**: Renames folders predictably using custom prefixes and sequential integers.
- **Custom Prefixes & Counters**: Flexible customization for starting index (`--start`) and string prefix (`--prefix`).
- **Dynamic Zero Padding**: Automatically maintains consistent digit alignment across items (e.g. `001`, `002`, `003` or `1000`, `1001`).
- **Dry-Run Preview**: Preview every rename transformation safely before executing disk writes (`--dry-run`).
- **Persistent Undo Engine**: Revert the last rename operation cleanly (`--undo`), with history persisting across application restarts.
- **Hidden & System Folder Protection**: Automatically ignores dotfiles (`.git`, `.vscode`), system folders, and Windows hidden folders via Win32 `GetFileAttributesW`.
- **Duplicate Collision Protection**: Skips renaming if target destination names already exist on disk.
- **Real-time Progress Indicator**: Outputs clear step status (`[1/25] 4%`) during processing.
- **Colored Terminal Output**: Visual status feedback using ANSI colors (Green for success, Yellow for warnings/skips, Blue for info, Red for errors) with automatic VT100 console setup.
- **Zero Third-Party Dependencies**: Pure Python 3.11+ standard library implementation.

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

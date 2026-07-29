# Architecture Overview - folder-auto-renamer

## Design Philosophy

The `folder-auto-renamer` project is designed as a lightweight, zero-dependency, professional command-line utility for Windows and cross-platform automation.

Key principles:
1. **Zero External Dependencies**: Standard Python Library only (`argparse`, `os`, `sys`, `pathlib`, `json`, `logging`, `ctypes`, `unittest`).
2. **Safety First**: Dry-run previewing, collision protection, and persistent history tracking prevent data loss.
3. **Modularity**: Strict separation of concerns across dedicated modules.

## Module Structure

```
src/folder_auto_renamer/
├── __init__.py        Package declaration and version info
├── __main__.py        Python executable entry point (-m)
├── cli.py             CLI argument parsing and handler dispatch
├── renamer.py         Core batch renaming execution engine
├── scanner.py         Directory scanning and hidden folder filtering
├── undo.py            Persistent undo history state engine
├── logger.py          Centralized logging configuration
├── colors.py          ANSI terminal color handling with VT100 auto-detection
├── progress.py        Terminal progress tracker and percentage formatter
├── config.py          Configuration data classes
├── utils.py           Windows API ctypes utilities & zero-padding math
└── exceptions.py      Custom exception hierarchy
```

## Architectural Data Flow

```
[CLI Command] 
     │
     ▼
┌───────────┐     Parses Flags
│  cli.py   ├────────────────────────┐
└─────┬─────┘                        │
      │ Validates Config             │
      ▼                              ▼
┌───────────┐                 ┌─────────────┐
│ config.py │                 │  logger.py  │
└─────┬─────┘                 └──────┬──────┘
      │                              │
      ▼                              │
┌──────────────┐                     │
│  renamer.py  │◄────────────────────┘
└──────┬───────┘
       │
       ├──► ┌─────────────┐   Discovers Eligible Folders
       │    │ scanner.py  ├──► (Filters Windows Hidden & Dotfiles)
       │    └─────────────┘
       │
       ├──► ┌─────────────┐   Formats Zero-Padded Names
       │    │  utils.py   ├──► (Calculates Dynamic Digits)
       │    └─────────────┘
       │
       ├──► ┌─────────────┐   Executes / Previews Rename
       │    │ progress.py ├──► Prints [1/25] 4% Progress
       │    └─────────────┘
       │
       └──► ┌─────────────┐   Saves History JSON
            │   undo.py   ├──► (~/.folder_auto_renamer_history.json)
            └─────────────┘
```

## Core Mechanics

### 1. Zero-Padding Algorithm
Calculates digit count using `max(3, len(str(start_number + total_items - 1)))`.
This guarantees that starting from 1 with 4 items yields `001, 002, 003, 004`, while starting from 1000 with 4 items yields `1000, 1001, 1002, 1003` without losing digit alignment.

### 2. Windows Hidden Folder Detection
Uses Windows Win32 API call `ctypes.windll.kernel32.GetFileAttributesW` to inspect bit flags:
- `FILE_ATTRIBUTE_HIDDEN` (`0x2`)
- `FILE_ATTRIBUTE_SYSTEM` (`0x4`)

Combined with Unix dotfile naming conventions (`.git`, `.cache`), system directories are safely ignored.

### 3. Persistent Undo Engine
When renames complete, session mappings `(old_name, new_name, old_path, new_path)` are appended to `~/.folder_auto_renamer_history.json`.
Running `folder-auto-renamer --undo` loads the latest session and iterates through items in reverse sequence to avoid path conflicts while restoring folder names.

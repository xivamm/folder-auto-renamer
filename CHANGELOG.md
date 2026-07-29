# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-07-29

### Added
- **Regex Search & Replace Mode**: Advanced regular expression pattern matching and capture group substitution.
- **Regex Template Presets**: 1-click preset buttons for removing numbers, formatting date prefixes, and sanitizing slugs.
- **Creation/Modification Date Injection Mode**: Prepend or append folder Creation or Modification timestamps.
- **Pattern Subfolder Filtering**: Filter target directories using wildcard (`*2026*`) patterns.
- **Windows File Explorer Context Menu Integration**: 1-click registration of "Open in Auto Folder Renamer Pro" in Explorer right-click context menu.
- **GitHub Star / Fork Header Buttons**: Direct header link button to repository.
- **GitHub Actions CI/CD Pipeline (`.github/workflows/ci.yml`)**: Automated cross-Python unit testing and executable asset build releases.
- **Shields.io Repository Badges**: Added build status, license, python version, and zero-dependency badges to `README.md`.
- **Unit Test Expansion**: Added `tests/test_regex_date.py` covering Regex replace, Date injection, and wildcard folder filtering.

## [1.1.0] - 2026-07-29


### Added
- Native Tkinter Desktop GUI (`gui.py`) with zero third-party dependencies.
- 10 renaming modes: Sequential, Replace Text, Add Prefix, Add Suffix, Uppercase, Lowercase, Title Case, Remove Spaces, Replace Spaces with Underscore, and Clean Special Characters.
- Real-time Treeview Live Preview table displaying current vs proposed folder names with status indicators and search filter.
- Dark mode and light mode theme toggle.
- One-click presets (Camera Photos, YouTube Projects, School Files, Client Projects, Documents).
- Sorting options prior to rename (Alphabetical, Date Created, Date Modified, Folder Size).
- Auto-indexing collision resolution strategy (e.g. `Folder (1)`).
- Recursive subfolder inclusion option and empty/non-empty folder filtering.
- CSV export functionality for undo history logs.
- Settings persistence saving last target path and dark mode toggle state to `~/.folder_auto_renamer_gui_settings.json`.
- Comprehensive unittest expansion in `tests/test_modes.py`.

## [1.0.0] - 2026-07-29


### Added
- Core sequential folder auto-renaming engine with configurable prefix and starting number.
- Automatic zero-padding algorithm ensuring digit consistency across folder batches.
- Preview mode (`--dry-run`) to test renaming operations without modifying disk files.
- Safe persistent undo system (`--undo`) surviving application restarts.
- Windows hidden folder and system directory filter (`GetFileAttributesW` attribute inspection + dotfile exclusion).
- Duplicate target protection skipping existing folder collisions.
- Progress percentage indicator (`[1/25] 4%`) for batch execution.
- Cross-platform ANSI terminal coloring with auto-detection for Windows VT100 console mode.
- Persistent file logging to `logs/folder-auto-renamer.log` using standard Python `logging`.
- Comprehensive unittest test suite covering scanner, renamer, zero-padding, hidden folders, and undo engine.

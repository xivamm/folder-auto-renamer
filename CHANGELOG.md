# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

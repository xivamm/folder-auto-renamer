"""Command-line interface parser and main program runner."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from folder_auto_renamer.colors import red
from folder_auto_renamer.config import RenamerConfig
from folder_auto_renamer.exceptions import FolderAutoRenamerError
from folder_auto_renamer.renamer import FolderRenamer


def create_parser() -> argparse.ArgumentParser:
    """Constructs and returns the argparse parser for folder-auto-renamer CLI.

    Returns:
        argparse.ArgumentParser: Configured argument parser object.
    """
    parser = argparse.ArgumentParser(
        prog="folder-auto-renamer",
        description="Automatically rename folders with intelligent sequential naming.",
        epilog="Examples:\n"
        "  folder-auto-renamer D:\\Pictures\n"
        "  folder-auto-renamer D:\\Pictures --prefix IMG-\n"
        "  folder-auto-renamer D:\\Pictures --prefix Client- --start 101\n"
        "  folder-auto-renamer D:\\Pictures --dry-run\n"
        "  folder-auto-renamer --undo\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        type=str,
        help="Target directory path containing subfolders to rename.",
    )

    parser.add_argument(
        "--prefix",
        type=str,
        default="Project-",
        help="Custom prefix for renamed folders (default: 'Project-').",
    )

    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Starting number for sequential folder counter (default: 1).",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview every rename action without making filesystem changes.",
    )

    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the last folder rename operation.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed verbose output for troubleshooting.",
    )

    return parser


def parse_args_to_config(args: argparse.Namespace) -> RenamerConfig:
    """Converts parsed command-line arguments into a RenamerConfig object.

    Args:
        args: Parsed argparse namespace.

    Returns:
        RenamerConfig: Validated application configuration.

    Raises:
        ValueError: If path is missing when --undo is not specified.
    """
    target_path = Path(args.path) if args.path else None

    if not args.undo and not target_path:
        raise ValueError("Target directory path is required unless --undo is specified.")

    config = RenamerConfig(
        target_path=target_path,
        prefix=args.prefix,
        start=args.start,
        dry_run=args.dry_run,
        undo=args.undo,
        verbose=args.verbose,
    )
    config.validate()
    return config


def main(cli_args: Optional[List[str]] = None) -> int:
    """Main entrypoint for CLI execution.

    Args:
        cli_args: List of command-line argument strings (defaults to sys.argv[1:]).

    Returns:
        int: Process exit code (0 for success, non-zero for error).
    """
    parser = create_parser()
    parsed_args = parser.parse_args(cli_args)

    try:
        config = parse_args_to_config(parsed_args)
        renamer = FolderRenamer(config)
        renamer.run()
        return 0

    except KeyboardInterrupt:
        print(red("\nOperation cancelled by user."))
        return 130
    except (FolderAutoRenamerError, ValueError) as err:
        print(red(f"Error: {err}"))
        return 1
    except Exception as err:
        print(red(f"Unexpected error: {err}"))
        return 1


if __name__ == "__main__":
    sys.exit(main())

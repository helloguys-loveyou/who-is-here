#!/usr/bin/env python3
"""Directory Pulse: print a compact overview of files in a directory."""

from __future__ import annotations

import argparse
from pathlib import Path


def format_size(size: int) -> str:
    """Format a byte count as a compact human-readable value."""
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{size} B"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def scan(directory: Path, limit: int) -> list[tuple[int, str]]:
    """Return the largest files under directory, sorted by byte size."""
    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    files: list[tuple[int, str]] = []
    for path in directory.rglob("*"):
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(directory).parts):
            try:
                size = path.stat().st_size
            except OSError:
                continue
            files.append((size, str(path.relative_to(directory))))

    files.sort(key=lambda item: (-item[0], item[1].lower()))
    return files[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Show the largest non-hidden files in a directory."
    )
    parser.add_argument("directory", nargs="?", default=".", help="directory to inspect")
    parser.add_argument("-n", "--limit", type=int, default=10, help="number of files to show")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    directory = Path(args.directory).expanduser().resolve()

    try:
        files = scan(directory, args.limit)
    except ValueError as error:
        parser.error(str(error))

    print(f"Directory Pulse: {directory}")
    print(f"Showing up to {args.limit} largest non-hidden files\n")

    if not files:
        print("No visible files found.")
        return

    name_width = max(len(name) for _, name in files)
    for size, name in files:
        print(f"{format_size(size):>10}  {name}")


if __name__ == "__main__":
    main()

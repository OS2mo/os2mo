#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""Helpers for file access."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from pathlib import Path
from typing import Union

from mora import config
from mora import exceptions

# --------------------------------------------------------------------------------------
# File helpers
# --------------------------------------------------------------------------------------


def get_export_dir() -> Path:
    """Get the configured export directory.

    Raises:
        E_DIR_NOT_FOUND: If the configured directory does not exist.

    Returns:
        A Path object pointing to the directory.
    """
    settings = config.get_settings()
    export_dir = Path(settings.query_export_dir)
    if not export_dir.is_dir():
        exceptions.ErrorCodes.E_DIR_NOT_FOUND()
    return export_dir


def list_files() -> set[str]:
    """Set export files.

    Raises:
        E_DIR_NOT_FOUND: If the configured directory does not exist.

    Returns:
        Set of filenames.
    """
    export_dir = get_export_dir()
    dir_contents = export_dir.iterdir()
    files = filter(lambda file: file.is_file(), dir_contents)
    filenames = set(map(lambda file: file.name, files))
    return filenames


def save_file(file_name: str, data: bytes, force: bool) -> None:
    """Save an export file with a given name.

    Args:
        file_name: Name of the export file.
        data: The file contents.
        force: Whether to override existing file.

    Raises:
        E_DIR_NOT_FOUND: If the configured directory does not exist.
        E_ALREADY_EXISTS: If the file already exists, and force is not set.

    Returns:
        None
    """
    export_dir = get_export_dir()
    file_path = export_dir / file_name
    # Protection against "../" in file_name, whatever path we get should be an
    # immediate child of the export_dir
    if file_path.parent != export_dir:
        exceptions.ErrorCodes.E_INVALID_INPUT(filename=file_name)

    if file_path.is_file() and not force:
        exceptions.ErrorCodes.E_ALREADY_EXISTS(filename=file_name)

    with file_path.open("wb") as f:
        f.write(data)


def load_file(file_name: str, binary: bool = False) -> Union[str, bytes]:
    """Load an export file with a given name.

    Args:
        file_name: Name of the export file.

    Raises:
        E_DIR_NOT_FOUND: If the configured directory does not exist.
        E_NOT_FOUND: If the file does not exist.

    Returns:
        The file contents as bytes
    """
    # Ensure that file exists in listing
    # This protects against paths containing "../"
    if file_name not in list_files():
        exceptions.ErrorCodes.E_NOT_FOUND(filename=file_name)

    mode = "rb" if binary else "r"
    export_dir = get_export_dir()
    file_path = export_dir / file_name
    with file_path.open(mode) as f:
        return f.read()

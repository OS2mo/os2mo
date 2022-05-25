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

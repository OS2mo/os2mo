# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import pytest
from aioresponses import aioresponses as aioresponses_


@pytest.fixture
def aioresponses():
    """Pytest fixture for aioresponses."""
    with aioresponses_() as aior:
        yield aior

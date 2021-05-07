#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import pytest

from ramodels.mo._shared import MOBase

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


class TestMOBase:
    def test_init(self):
        # MOBase cannot be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            MOBase()

    def test_fields(self):
        # Subclasses of MOBase should have a UUID field
        class MOSub(MOBase):
            pass

        assert MOSub.__fields__.get("uuid")

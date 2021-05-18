#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import datetime

from ramodels.mo.employee import Employee


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestEmployee:
    def test_required_fields(self):
        # Fails if new required fields are added or existing is removed
        assert Employee(
            name="Anders And",
        )

    def test_optional_fields(self):
        # Fails if an optional field is removed
        assert Employee(
            type="employee",
            name="Anders And",
            cpr_no="0707614285",
            seniority=datetime(year=2021, month=5, day=12),
        )

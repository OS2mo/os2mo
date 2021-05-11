#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import uuid4

from ramodels.mo.facet import FacetClass

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestFacetClass:
    def test_required_fields(self):
        """Fails if new required fields are added or existing is removed"""
        assert FacetClass(name="Direktør", user_key="Direktør", org_uuid=uuid4())

    def test_optional_fields(self):
        """Fails if an optional field is removed"""
        assert FacetClass(
            name="Direktør", user_key="Direktør", scope="TEXT", org_uuid=uuid4()
        )

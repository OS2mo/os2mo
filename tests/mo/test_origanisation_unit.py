#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

from ramodels.mo._shared import OrgUnitHierarchy
from ramodels.mo._shared import OrgUnitLevel
from ramodels.mo._shared import OrgUnitType
from ramodels.mo._shared import ParentRef
from ramodels.mo._shared import Validity
from ramodels.mo.organisation_unit import OrganisationUnit


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestOrganisationUnit:
    def test_required_fields(self):
        assert OrganisationUnit(
            type="org_unit",
            user_key="Andeby Kommune",
            validity=Validity(from_date="1930-01-01", to_date=None),
            name="Social og sundhed",
            org_unit_type=OrgUnitType(
                uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")
            ),
            org_unit_level=OrgUnitLevel(
                uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")
            ),
        )

    def test_optional_field(self):
        assert OrganisationUnit(
            type="org_unit",
            user_key="Andeby Kommune",
            validity=Validity(from_date="1930-01-01", to_date=None),
            name="Social og sundhed",
            parent=ParentRef(uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")),
            org_unit_hierarchy=OrgUnitHierarchy(
                uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")
            ),
            org_unit_type=OrgUnitType(
                uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")
            ),
            org_unit_level=OrgUnitLevel(
                uuid=UUID("26e30822-c9ee-4b5d-8412-bb28672a4d64")
            ),
        )

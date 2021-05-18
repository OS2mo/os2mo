#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import uuid4

from ramodels.mo._shared import AssociationType
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Validity
from ramodels.mo.association import Association


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestAssociation:
    def test_required_fields(self):
        assert Association(
            org_unit=OrgUnitRef(uuid=uuid4()),
            person=PersonRef(uuid=uuid4()),
            association_type=AssociationType(uuid=uuid4()),
            validity=Validity(from_date="1930-01-01", to_date=None),
        )

    def test_optional_fields(self):
        assert Association(
            type="association",
            org_unit=OrgUnitRef(uuid=uuid4()),
            person=PersonRef(uuid=uuid4()),
            association_type=AssociationType(uuid=uuid4()),
            validity=Validity(from_date="1930-01-01", to_date=None),
        )

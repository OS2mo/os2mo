#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import uuid4

from ramodels.mo import Manager
from ramodels.mo._shared import ManagerLevel
from ramodels.mo._shared import ManagerType
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Responsibility
from ramodels.mo._shared import Validity


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestManager:
    def test_required_fields(self):
        assert Manager(
            org_unit=OrgUnitRef(uuid=uuid4()),
            person=PersonRef(uuid=uuid4()),
            responsibility=[Responsibility(uuid=uuid4())],
            manager_level=ManagerLevel(uuid=uuid4()),
            manager_type=ManagerType(uuid=uuid4()),
            validity=Validity(from_date="1930-01-01", to_date=None),
        )

    def test_optional_fields(self):
        assert Manager(
            type="manager",
            org_unit=OrgUnitRef(uuid=uuid4()),
            person=PersonRef(uuid=uuid4()),
            responsibility=[Responsibility(uuid=uuid4())],
            manager_level=ManagerLevel(uuid=uuid4()),
            manager_type=ManagerType(uuid=uuid4()),
            validity=Validity(from_date="1930-01-01", to_date=None),
        )

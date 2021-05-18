#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import uuid4

from ramodels.mo._shared import AddressType
from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import OrganisationRef
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Validity
from ramodels.mo._shared import Visibility
from ramodels.mo.address import Address


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


class TestAddress:
    def test_required_fields(self):
        assert Address(
            value="andersand@andeby.dk",
            address_type=AddressType(uuid=uuid4()),
            org=OrganisationRef(uuid=uuid4()),
            validity=Validity(from_date="1930-01-01", to_date=None),
        )

    def test_optional_fields(self):
        assert Address(
            type="address",
            value="andersand@andeby.dk",
            value2="andersineand@andeby.dk",
            address_type=AddressType(uuid=uuid4()),
            org=OrganisationRef(uuid=uuid4()),
            person=PersonRef(uuid=uuid4()),
            org_unit=OrgUnitRef(uuid=uuid4()),
            engagement=EngagementRef(uuid=uuid4()),
            validity=Validity(from_date="1930-01-01", to_date=None),
            visibility=Visibility(uuid=uuid4()),
        )

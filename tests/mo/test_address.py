#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import UUID

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
        """Will break if Required fields become Optional"""
        assert Address(
            type="address",
            value="andersand@andeby.dk",
            address_type=AddressType(uuid=UUID("f376deb8-4743-4ca6-a047-3241de8fe9d2")),
            org=OrganisationRef(uuid=UUID("5b3a55b1-958c-416e-9054-606b2c9e4fcd")),
            validity=Validity(from_date="1930-01-01", to_date=None),
        )

    def test_optional_fields(self):
        assert Address(
            type="address",
            value="andersand@andeby.dk",
            value2="andersineand@andeby.dk",
            address_type=AddressType(uuid=UUID("f376deb8-4743-4ca6-a047-3241de8fe9d2")),
            org=OrganisationRef(uuid=UUID("5b3a55b1-958c-416e-9054-606b2c9e4fcd")),
            person=PersonRef(uuid=UUID("65def1a8-2816-4f59-b3ee-3b67a1b99952")),
            org_unit=OrgUnitRef(uuid=UUID("3b866d97-0b1f-48e0-8078-686d96f430b3")),
            engagement=EngagementRef(uuid=UUID("3b866d97-0b1f-48e0-8078-686d96f430b3")),
            validity=Validity(from_date="1930-01-01", to_date=None),
            visibility=Visibility(uuid=UUID("3b866d97-0b1f-48e0-8078-686d96f430b3")),
        )

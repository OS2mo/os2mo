# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Test the dataclasses derived from the filters."""

from uuid import UUID

import pytest
from strawberry import UNSET

from mora.graphapi.filter_dataclasses import AddressFilterData
from mora.graphapi.filter_dataclasses import ClassFilterData
from mora.graphapi.filter_dataclasses import OrganisationUnitFilterData
from mora.graphapi.filter_dataclasses import strawberry2dataclass
from mora.graphapi.filters import AddressFilter
from mora.graphapi.filters import ClassFilter
from mora.graphapi.filters import OrganisationUnitFilter

FILTER_UUID = UUID("b7441235-3418-485b-9d14-db6bc1ebe211")


def test_builds_the_filter_a_query_would_have() -> None:
    """Test that a filter built from the outside, as a policy would, converts."""
    filter = AddressFilterData(
        uuids=[FILTER_UUID],
        address_type=ClassFilterData(user_keys=["EmailEmployee"]),
        org_unit=OrganisationUnitFilterData(
            ancestor=OrganisationUnitFilterData(uuids=[FILTER_UUID])
        ),
    )
    assert filter.uuids == [FILTER_UUID]
    assert filter.address_type.user_keys == ["EmailEmployee"]
    # the filters refer to each other in cycles; the nesting still holds
    assert filter.org_unit.ancestor.uuids == [FILTER_UUID]
    # a field that was not given keeps the sentinel, rather than becoming null
    assert filter.from_date is UNSET
    # the filter a GraphQL query produces converts to the very same thing
    assert filter == strawberry2dataclass(
        AddressFilter(
            uuids=[FILTER_UUID],
            address_type=ClassFilter(user_keys=["EmailEmployee"]),
            org_unit=OrganisationUnitFilter(
                ancestor=OrganisationUnitFilter(uuids=[FILTER_UUID])
            ),
        )
    )


def test_unknown_field_is_rejected() -> None:
    """Test that a mistyped field is rejected, rather than dropped."""
    with pytest.raises(TypeError, match="unexpected keyword argument 'uuid'"):
        AddressFilterData(uuid=[FILTER_UUID])

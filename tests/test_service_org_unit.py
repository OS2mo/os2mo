# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import pytest

from mora import lora
from mora.handler.impl.association import AssociationReader
from mora.service.orgunit import UnitDetails
from mora.service.orgunit import get_one_orgunit
from tests import util


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@util.patch_query_args()
async def test_get_one_orgunit_with_association_count() -> None:
    _connector = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    orgunit = await get_one_orgunit(
        _connector,
        "2874e1dc-85e6-4269-823a-e1125484dfd3",
        count_related={"association": AssociationReader},
    )
    assert orgunit is not None
    assert "association_count" in orgunit


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "details,expected_keys",
    [
        (
            UnitDetails.NCHILDREN,
            {"uuid", "name", "user_key", "validity", "child_count"},
        ),
        (UnitDetails.PATH, {"uuid", "name", "user_key", "validity", "location"}),
    ],
)
@util.patch_query_args()
async def test_details(details: UnitDetails, expected_keys: set[str]) -> None:
    _connector = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    orgunit = await get_one_orgunit(
        _connector, "2874e1dc-85e6-4269-823a-e1125484dfd3", details=details
    )
    assert orgunit is not None
    assert set(orgunit.keys()) == expected_keys

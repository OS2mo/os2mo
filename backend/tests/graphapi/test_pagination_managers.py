# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from uuid import UUID

import pytest

from tests.conftest import GraphAPIPost


@pytest.fixture
def read_managers(
    graphapi_post: GraphAPIPost,
) -> Callable[[UUID, str | None], str | None]:
    """Retrieves the next pagination cursor for a managers query with an ancestor filter."""

    def inner(ancestor_uuid: UUID, cursor: str | None) -> str | None:
        query = """
        query Manager($cursor: Cursor, $ancestor_uuids: [UUID!]) {
          managers(
            cursor: $cursor
            limit: 100
            filter: {
              org_unit: {ancestor: {uuids: $ancestor_uuids}}
            }
          ) {
            page_info { next_cursor }
          }
        }
        """
        # Variables must be converted to strings for GraphQL
        response = graphapi_post(
            query, {"cursor": cursor, "ancestor_uuids": [str(ancestor_uuid)]}
        )
        assert response.errors is None
        assert response.data is not None

        return response.data["managers"]["page_info"]["next_cursor"]

    return inner


@pytest.fixture
def create_org_unit_with_validity(
    root_org: UUID,
    graphapi_post: GraphAPIPost,
) -> Callable[[datetime, datetime | None], UUID]:
    """Provisions organization units with specific validity bounds."""

    def inner(start: datetime, end: datetime | None = None) -> UUID:
        validity = {
            "from": start.isoformat(),
            "to": end.isoformat() if end else None,
        }

        query = """
        mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
            org_unit_create(input: $input) {
                uuid
            }
        }
        """
        response = graphapi_post(
            query,
            variables={
                "input": {
                    "name": "Dated Unit",
                    "user_key": "dated_unit",
                    "parent": None,
                    "validity": validity,
                    # Arbitrary hardcoded UUID used for greppability
                    "org_unit_type": "8f7be3e7-b695-49e6-b9da-86a4266417bd",
                }
            },
        )
        assert response.errors is None
        assert response.data is not None
        return UUID(response.data["org_unit_create"]["uuid"])

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_terminates_when_known(
    read_managers: Callable[[UUID, str | None], str | None],
    create_org_unit_with_validity: Callable[[datetime, datetime | None], UUID],
) -> None:
    """Test that pagination terminates correctly after exactly 2 iterations when using a known ancestor UUID."""
    root_ou = create_org_unit_with_validity(datetime(1970, 1, 1), None)

    # First page is empty but returns a cursor for the next page
    cursor = read_managers(root_ou, None)
    assert cursor is not None

    # Second page is empty and correctly terminates
    cursor = read_managers(root_ou, cursor)
    assert cursor is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_terminates_when_unknown(
    read_managers: Callable[[UUID, str | None], str | None],
    root_org: UUID,
) -> None:
    """Test that pagination terminates when using an unknown ancestor UUID."""
    # Arbitrary hardcoded UUID used for greppability
    unknown_uuid = UUID("8f7be3e7-b695-49e6-b9da-86a4266417bd")

    # Immediate termination expected
    cursor = read_managers(unknown_uuid, None)
    assert cursor is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "start,end",
    [
        # Terminated in the past
        (datetime(1970, 1, 1), datetime(2020, 1, 1)),
        # Starts in the future
        (datetime(3000, 1, 1), None),
    ],
)
async def test_terminates_with_validity(
    read_managers: Callable[[UUID, str | None], str | None],
    create_org_unit_with_validity: Callable[[datetime, datetime | None], UUID],
    start: datetime,
    end: datetime | None,
) -> None:
    """Test that pagination terminates regardless of ancestor org-unit validity."""
    invalid_ou_uuid = create_org_unit_with_validity(start, end)

    # Immediate termination expected
    cursor = read_managers(invalid_ou_uuid, None)
    assert cursor is None

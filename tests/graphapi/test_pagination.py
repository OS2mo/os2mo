# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_keyset_pagination(
    graphapi_post: GraphAPIPost,
    create_facet: Callable[[dict[str, Any]], UUID],
    delete_facet: Callable[[UUID], None],
) -> None:
    zero_uuid = "00000000-0000-0000-0000-000000000000"
    one_uuid = "10000000-0000-0000-0000-000000000000"
    two_uuid = "20000000-0000-0000-0000-000000000000"
    three_uuid = "30000000-0000-0000-0000-000000000000"
    four_uuid = "40000000-0000-0000-0000-000000000000"
    five_uuid = "50000000-0000-0000-0000-000000000000"
    six_uuid = "60000000-0000-0000-0000-000000000000"
    f_uuid = "ffffffff-ffff-ffff-ffff-ffffffffffff"

    def create(uuid: str) -> None:
        create_facet(
            {
                "uuid": uuid,
                "user_key": uuid,
                "validity": {"from": "1999-06-07", "to": None},
            }
        )

    def get_page(limit: int, cursor: str | None) -> tuple[list[str], str | None]:
        query = """
            query GetPage($limit: int, $cursor: Cursor) {
              facets(limit: $limit, cursor: $cursor) {
                objects {
                  uuid
                }
                page_info {
                  next_cursor
                }
              }
            }
        """
        response = graphapi_post(query, dict(limit=limit, cursor=cursor))
        assert response.errors is None
        uuids = [obj["uuid"] for obj in response.data["facets"]["objects"]]
        return uuids, response.data["facets"]["page_info"]["next_cursor"]

    # Create facets spanning the entire UUID range, including both boundaries
    create(zero_uuid)
    # one_uuid will be added behind the cursor after we have started paging
    create(two_uuid)
    # three_uuid will be added ahead of the cursor after we have started paging
    create(four_uuid)
    create(five_uuid)
    create(six_uuid)
    create(f_uuid)

    # First page
    page_1, cursor = get_page(limit=2, cursor=None)
    assert page_1 == [zero_uuid, two_uuid]
    assert cursor is not None

    # Modify the data mid-pagination
    create(one_uuid)  # added behind the cursor: must not appear
    create(three_uuid)  # added ahead of the cursor: must appear
    delete_facet(UUID(five_uuid))  # removed before being reached: must not appear

    # Second page: modifications ahead of the cursor are reflected, those
    # behind it are not.
    page_2, cursor = get_page(limit=2, cursor=cursor)
    assert page_2 == [three_uuid, four_uuid]
    assert cursor is not None

    # Final page: exactly fills the limit, yet pagination terminates without an
    # extra empty page.
    page_3, cursor = get_page(limit=2, cursor=cursor)
    assert page_3 == [six_uuid, f_uuid]
    assert cursor is None

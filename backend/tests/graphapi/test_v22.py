# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_kle_number(graphapi_post: GraphAPIPost) -> None:
    """Test kle_number field."""
    # Create KLE number class
    kle_number = graphapi_post(
        """
        mutation CreateKleNumber {
          class_create(
            input: {
              facet_uuid: "27935dbb-c173-4116-a4b5-75022315749d",
              name: "number",
              user_key: "number",
              validity: { from: "2010-01-01", to: "2020-01-01" },
            }
          ) {
            uuid
          }
        }
        """
    )
    assert kle_number.errors is None
    assert kle_number.data is not None
    kle_number_uuid = kle_number.data["class_create"]["uuid"]

    # Create KLE
    kle = graphapi_post(
        """
        mutation CreateKle($number: UUID!) {
          kle_create(
            input: {
              org_unit: "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
              kle_aspects: ["9016d80a-c6d2-4fb4-83f1-87ecc23ab062"],
              kle_number: $number,
              validity: { from: "2025-01-01" },
            }
          ) {
            uuid
          }
        }
        """,
        variables={"number": kle_number_uuid},
    )
    assert kle.errors is None
    assert kle.data is not None
    kle_uuid = kle.data["kle_create"]["uuid"]

    # Read KLE
    query = """
        query ReadKLE($filter: KLEFilter!) {
          kles(filter: $filter) {
            objects {
              current {
                kle_number {
                  name
                }
              }
            }
          }
        }
    """

    # GraphQL v22 incorrectly assumed that KLE-number classes were static;
    # valid from -infinity to infinity and never changing. Attempting to read a
    # with a kle_number in the past or future would therefore lead to an error,
    # since the promise of always returning a single KLE class could not be
    # fulfilled.
    response_v23 = graphapi_post(
        query,
        variables={"filter": {"uuids": kle_uuid}},
        url="/graphql/v22",
    )
    assert response_v23.errors == [
        {
            "message": "too few items in iterable (expected 1)",
            "locations": [{"line": 6, "column": 17}],
            "path": ["kles", "objects", 0, "current", "kle_number"],
        }
    ]

    # GraphQL v23 returns a -- potentially empty -- list of classes valid in
    # the given time period.
    response_v23 = graphapi_post(
        query,
        variables={"filter": {"uuids": kle_uuid}},
        url="/graphql/v23",
    )
    assert response_v23.errors is None
    assert response_v23.data == {"kles": {"objects": [{"current": {"kle_number": []}}]}}

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from unittest import TestCase

import pytest
from fastapi.encoders import jsonable_encoder
from mora.graphapi.versions.latest.resolvers import get_date_interval
from strawberry import UNSET

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_dates(graphapi_post: GraphAPIPost):
    """Test that GraphQL dates are passed correctly."""
    facet_create = graphapi_post(
        """
        mutation CreateFacet {
          facet_create(input: {user_key: "test", validity: {from: null, to: null}}) {
            uuid
          }
        }
        """
    )
    facet_uuid = facet_create.data["facet_create"]["uuid"]

    def create_class(parent, from_date, to_date) -> str:
        r = graphapi_post(
            """
                mutation CreateClass(
                  $facet_uuid: UUID!,
                  $parent_uuid: UUID,
                  $from_date: DateTime,
                  $to_date: DateTime,
                ) {
                  class_create(
                    input: {
                      facet_uuid: $facet_uuid,
                      parent_uuid: $parent_uuid,
                      name: "test",
                      user_key: "test",
                      validity: {from: $from_date, to: $to_date}
                    }
                  ) {
                    uuid
                  }
                }
            """,
            variables=jsonable_encoder(
                {
                    "facet_uuid": facet_uuid,
                    "parent_uuid": parent,
                    "from_date": from_date,
                    "to_date": to_date,
                }
            ),
        )
        return r.data["class_create"]["uuid"]

    before = create_class(None, None, "2000-01-01")  # noqa
    after = create_class(None, "2000-01-05", None)
    after_10_days = create_class(after, "2000-01-10", "2000-01-15")
    after_20_days = create_class(after, "2000-01-20", "2000-01-25")

    query = """
        query TestQuery($facet_uuid: UUID!) {
          classes(
            filter: {from_date: "2000-01-05", to_date: null, facet: {uuids: [$facet_uuid]}}
          ) {
            objects {
              objects {
                uuid
                children(filter: {from_date: "2000-01-05", to_date: "2000-01-15"}) {
                  uuid
                }
              }
            }
          }
        }
    """
    response = graphapi_post(query, variables={"facet_uuid": facet_uuid})
    assert response.errors is None
    TestCase().assertCountEqual(
        response.data["classes"]["objects"],
        [
            {"objects": [{"uuid": after_10_days, "children": []}]},
            {"objects": [{"uuid": after_20_days, "children": []}]},
            {
                "objects": [
                    {
                        "uuid": after,
                        "children": [
                            {"uuid": after_10_days},
                        ],
                    }
                ]
            },
        ],
    )


def test_get_date_interval_from_less_than_to() -> None:
    with pytest.raises(
        ValueError,
        match=r"from_date .* must be less than or equal to to_date .*",
    ):
        get_date_interval(
            from_date=datetime(2000, 1, 1),
            to_date=datetime(1900, 1, 1),
        )


def test_get_date_interval_from_none_to_unset() -> None:
    with pytest.raises(
        ValueError,
        match="Cannot infer UNSET to_date from interval starting at -infinity",
    ):
        get_date_interval(from_date=None, to_date=UNSET)

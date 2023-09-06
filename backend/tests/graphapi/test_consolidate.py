# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_consolidate_feature_flag(
    graphapi_post: Callable, set_settings: Callable[..., None]
) -> None:
    # Create org unit
    org_unit_create_mutation = """
        mutation OrgUnitCreate {
          org_unit_create(
            input: {
              org_unit_type: "51203743-f2db-4f17-a7e1-fee48c178799",
              validity: {from: "2000-01-01", to: "2000-12-31"},
              name: "Foo",
            }
          ) {
            uuid
          }
        }
    """
    org_unit_create = graphapi_post(org_unit_create_mutation)
    org_unit_uuid = org_unit_create.data["org_unit_create"]["uuid"]

    # Update it with the same name twice
    org_unit_update_mutation = """
        mutation OrgUnitUpdate($uuid: UUID!, $from: DateTime!, $to: DateTime!) {
          org_unit_update(
            input: {uuid: $uuid, name: "Bar", validity: {from: $from, to: $to}}
          ) {
            uuid
          }
        }
    """
    graphapi_post(
        org_unit_update_mutation,
        {"uuid": org_unit_uuid, "from": "2000-02-01", "to": "2000-12-31"},
    )
    graphapi_post(
        org_unit_update_mutation,
        {"uuid": org_unit_uuid, "from": "2000-03-01", "to": "2000-12-31"},
    )

    # Check that response is consolidated if enabled
    org_unit_read_query = """
        query OrgUnitRead($uuids: [UUID!]) {
          org_units(filter: {uuids: $uuids, from_date: null, to_date: null}) {
            objects {
              objects {
                name
                validity {
                  from
                  to
                }
              }
            }
          }
        }
    """
    response = graphapi_post(org_unit_read_query, dict(uuids=org_unit_uuid))
    assert response.data["org_units"]["objects"][0]["objects"] == [
        {
            "name": "Foo",
            "validity": {
                "from": "2000-01-01T00:00:00+01:00",
                "to": "2000-01-31T00:00:00+01:00",
            },
        },
        {
            "name": "Bar",
            "validity": {
                "from": "2000-02-01T00:00:00+01:00",
                "to": "2000-12-31T00:00:00+01:00",
            },
        },
    ]

    # Check that response is not consolidated if disabled
    set_settings(CONSOLIDATE=False)
    response = graphapi_post(org_unit_read_query, dict(uuids=org_unit_uuid))
    assert response.data["org_units"]["objects"][0]["objects"] == [
        {
            "name": "Foo",
            "validity": {
                "from": "2000-01-01T00:00:00+01:00",
                "to": "2000-01-31T00:00:00+01:00",
            },
        },
        {
            "name": "Bar",
            "validity": {
                "from": "2000-02-01T00:00:00+01:00",
                "to": "2000-02-29T00:00:00+01:00",
            },
        },
        {
            "name": "Bar",
            "validity": {
                "from": "2000-03-01T00:00:00+01:00",
                "to": "2000-12-31T00:00:00+01:00",
            },
        },
    ]

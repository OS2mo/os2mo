# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import one

DEFAULT_TIMEZONE = ZoneInfo("Europe/Copenhagen")


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_writing_registration(graphapi_post) -> None:
    """Integrationtest for reading and writing registrations."""
    query = """
        query ReadObjectRegistration($uuid: UUID!) {
          org_units(filter: {uuids: [$uuid]}) {
            objects {
              uuid
              registrations {
                registration_id
                start
                end
              }
            }
          }
        }
    """
    uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    # Fetch the current registrations
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit["uuid"] == uuid

    # We cannot assert anything meaningful about the registration_id at this point, as
    # the ID is derived from a postgresql id sequence
    registration = one(org_unit["registrations"])
    assert registration["end"] is None

    # Update the org-unit to create a new registration
    response = graphapi_post(
        """
            mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
                org_unit_update(input: $input) {
                    uuid
                }
            }
        """,
        {
            "input": {
                "uuid": uuid,
                "validity": {"from": "2050-01-01"},
                "name": str(uuid4()),
            }
        },
    )
    assert response.errors is None
    assert response.data == {"org_unit_update": {"uuid": uuid}}

    # Fetch registrations now, expecting to find one more
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit["uuid"] == uuid

    # We expect exactly two registrations now
    old_registration, new_registration = org_unit["registrations"]
    # with the old registration being the same as before, but end is no longer None
    assert old_registration["registration_id"] == registration["registration_id"]
    assert old_registration["start"] == registration["start"]
    assert old_registration["end"] is not None
    # as the new registration has the None instead
    assert new_registration["end"] is None
    assert new_registration["registration_id"] > old_registration["registration_id"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_read_object_registration(graphapi_post) -> None:
    """Object registration reading integration-test."""
    query = """
        query ReadObjectRegistration($uuid: UUID!) {
          org_units(filter: {uuids: [$uuid]}) {
            objects {
              uuid
              registrations {
                actor
                model
                uuid
                start
                end
              }
            }
          }
        }
    """
    uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    # Fetch the current registrations
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    org_unit = one(response.data["org_units"]["objects"])
    assert org_unit["uuid"] == uuid

    registration = one(org_unit["registrations"])
    assert registration["actor"] == "05211100-baad-1110-006e-6f2075756964"
    assert registration["model"] == "org_unit"
    assert registration["uuid"] == uuid
    datetime.fromisoformat(registration["start"])
    assert registration["end"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_read_top_level_registration(graphapi_post) -> None:
    """Top-level registration reading integration-test."""
    query = """
        query ReadRegistration($uuid: UUID!) {
          registrations(filter: {uuids: [$uuid]}) {
            objects {
              actor
              model
              uuid
              start
              end
            }
          }
        }
    """
    uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"

    # Fetch the current registrations
    response = graphapi_post(query, {"uuid": uuid})
    assert response.errors is None
    assert response.data
    registration = one(response.data["registrations"]["objects"])

    assert registration["actor"] == "05211100-baad-1110-006e-6f2075756964"
    assert registration["model"] == "org_unit"
    assert registration["uuid"] == uuid
    datetime.fromisoformat(registration["start"])
    assert registration["end"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_read_registration_dates_filter_with_uuid(graphapi_post) -> None:
    """Registration dates filter integration-test."""
    # Create first registration
    response = graphapi_post(
        """
        mutation CreateEmployee {
          employee_create(input: {given_name: "Foo", surname: "Bar"}) {
            uuid
          }
        }
        """
    )
    assert response.errors is None
    employee_uuid = response.data["employee_create"]["uuid"]

    # Create second registration
    time.sleep(0.010)  # meh, but can't freezegun database's now()
    response = graphapi_post(
        """
        mutation UpdateEmployee($uuid: UUID!) {
          employee_update(
            input: {
              uuid: $uuid,
              given_name: "Foobar",
              validity: {from: "2020-01-01"}
            }
          ) {
            uuid
          }
        }
        """,
        {"uuid": employee_uuid},
    )
    assert response.errors is None

    def registrations(start, end):
        query = """
            query ReadRegistrations(
              $uuid: UUID!,
              $start: DateTime,
              $end: DateTime
            ) {
              registrations(
                filter: {
                  uuids: [$uuid],
                  start: $start,
                  end: $end
                }
              ) {
                objects {
                  start
                  end
                }
              }
            }
        """
        response = graphapi_post(
            query,
            jsonable_encoder(
                {
                    "uuid": employee_uuid,
                    "start": start,
                    "end": end,
                }
            ),
        )
        assert response.errors is None
        return response.data["registrations"]["objects"]

    r1, r2 = registrations(None, None)
    r1_start = datetime.fromisoformat(r1["start"])
    r1_end = datetime.fromisoformat(r1["end"])
    r2_start = datetime.fromisoformat(r2["start"])
    r2_end = r2["end"]
    assert r1_start < r1_end == r2_start
    assert r2_end is None

    ms = timedelta(milliseconds=1)
    min = date(year=1, month=1, day=2)  # why day=2? see commit 746d6535
    max = date(year=9999, month=12, day=31)

    # |--a--|
    #       |--b--|
    #             |--c--|
    #                  |-------d------
    #                         |---e---
    #           |----r1----|---r2-----
    # Filter contains all
    assert registrations(None, None) == [r1, r2]
    # Filter is before all (a)
    assert registrations(min, r1_start - ms) == []
    assert registrations(None, r1_start - ms) == []
    # Filter start is before all, end is within first (b)
    assert registrations(min, r1_start + ms) == [r1]
    assert registrations(None, r1_start + ms) == [r1]
    # Filter is contained within first (c)
    assert registrations(r1_start + ms, r1_end - ms) == [r1]
    # Filter start is within first, end is after all (d)
    assert registrations(r1_end - ms, max) == [r1, r2]
    assert registrations(r1_end - ms, None) == [r1, r2]
    # Filter start is after first, end is after all (e)
    assert registrations(r1_end + ms, max) == [r2]
    assert registrations(r1_end + ms, None) == [r2]
    # TODO: tests on boundary-values are difficult to do as long as now() is handled
    # by LoRa templates and cannot be injected.


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_read_registration_only_dates_filter(graphapi_post) -> None:
    """Registration dates filter integration-test."""
    start_of_test = datetime.now(tz=DEFAULT_TIMEZONE)
    response = graphapi_post(
        """
        mutation CreateEmployee {
          employee_create(input: {given_name: "Foo", surname: "Bar"}) {
            uuid
          }
        }
        """
    )
    assert response.errors is None
    employee_uuid = response.data["employee_create"]["uuid"]

    # Create second registration
    time.sleep(0.010)  # meh, but can't freezegun database's now()
    response = graphapi_post(
        """
        mutation UpdateEmployee($uuid: UUID!) {
          employee_update(
            input: {
              uuid: $uuid,
              given_name: "Foobar",
              validity: {from: "2020-01-01"}
            }
          ) {
            uuid
          }
        }
        """,
        {"uuid": employee_uuid},
    )
    assert response.errors is None

    def registrations(start, end):
        query = """
            query ReadRegistrations(
              $start: DateTime,
              $end: DateTime
            ) {
              registrations(
                filter: {
                  start: $start,
                  end: $end
                }
              ) {
                objects {
                  start
                  end
                }
              }
            }
        """
        response = graphapi_post(
            query,
            jsonable_encoder(
                {
                    "start": start,
                    "end": end,
                }
            ),
        )
        assert response.errors is None
        return response.data["registrations"]["objects"]

    all_registrations = registrations(None, None)
    assert len(all_registrations) > 2
    new_registrations = registrations(start_of_test, None)

    assert len(new_registrations) == 2

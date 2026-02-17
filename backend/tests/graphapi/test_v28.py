# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

import pytest
from mora.db import AsyncSession
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationEnhedTilsGyldighed
from mora.graphapi.version import Version
from mora.util import DEFAULT_TIMEZONE
from more_itertools import one
from sqlalchemy import select

from tests.conftest import GraphAPIPost


@pytest.mark.parametrize(
    "version",
    (
        Version.VERSION_28,
        Version.VERSION_29,
    ),
)
@pytest.mark.integration_test
async def test_off_by_zero_or_one(
    empty_db: AsyncSession,
    root_org: UUID,
    afdeling: UUID,
    graphapi_post: GraphAPIPost,
    version: Version,
) -> None:
    graphql_url = "/graphql/v28" if version == Version.VERSION_28 else "/graphql/v29"

    create = graphapi_post(
        """
        mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables={
            "input": {
                "org_unit_type": str(afdeling),
                "name": "create",
                "validity": {
                    "from": "2021-01-01T00:00:00+01:00",
                    "to": "2023-03-03T00:00:00+01:00",
                },
            }
        },
        url=graphql_url,
    )
    assert create.errors is None
    assert create.data is not None
    uuid = create.data["org_unit_create"]["uuid"]

    async def read_graphql() -> dict:
        r = graphapi_post(
            """
            query ReadOrgUnit($uuid: UUID!) {
              org_units(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  validities(start: null, end: null) {
                    name
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
            """,
            variables={
                "uuid": uuid,
            },
            url=graphql_url,
        )
        assert r.errors is None
        assert r.data is not None
        return one(r.data["org_units"]["objects"])

    async def read_sql() -> list[tuple[str, datetime | None, datetime | None]]:
        objs = await empty_db.scalars(
            select(OrganisationEnhedTilsGyldighed)
            .join(
                OrganisationEnhedRegistrering,
                OrganisationEnhedTilsGyldighed.organisationenhed_registrering_id
                == OrganisationEnhedRegistrering.id,
            )
            .where(OrganisationEnhedRegistrering.organisationenhed_id == uuid)
            .order_by(OrganisationEnhedTilsGyldighed.id)
        )
        return [
            (obj.gyldighed, obj.virkning_period.lower, obj.virkning_period.upper)
            for obj in objs
        ]

    # The dates returned by GraphQL are the same dates we created with in both
    # versions. But in v28, 2023-03-03 actually means 2023-03-04 23:59:59, or
    # more accurately, 2023-03-04T00:00:00+01:00, as we will see in the
    # database.
    read = await read_graphql()
    assert read == {
        "validities": [
            {
                "name": "create",
                "validity": {
                    "from": "2021-01-01T00:00:00+01:00",
                    "to": "2023-03-03T00:00:00+01:00",
                },
            }
        ]
    }

    # GraphQL v28 is lying, cause that's not actually what's in the database
    validities = await read_sql()
    if version == Version.VERSION_28:
        assert validities == [
            (
                "Aktiv",
                datetime(2021, 1, 1, 0, 0, 0, tzinfo=DEFAULT_TIMEZONE),
                datetime(2023, 3, 4, 0, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            )
        ]
        # The dates in the database are off-by-one
    else:
        # The dates in the database are the same dates we created with
        assert validities == [
            (
                "Aktiv",
                datetime(2021, 1, 1, 0, 0, 0, tzinfo=DEFAULT_TIMEZONE),
                datetime(2023, 3, 3, 0, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            )
        ]

    # Update
    graphapi_post(
        """
        mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
          org_unit_update(input: $input) {
            uuid
          }
        }
        """,
        variables={
            "input": {
                "uuid": uuid,
                "org_unit_type": str(afdeling),
                "name": "update",
                "validity": {
                    "from": "2022-02-02T00:00:00+01:00",
                    "to": "2024-04-04T00:00:00+01:00",
                },
            }
        },
        url=graphql_url,
    )

    read = await read_graphql()
    if version == Version.VERSION_28:
        # After the update, it is now apparent that we were lying. In GraphQL
        # v28, the 'to' date of the first validity is off-by-one.
        assert read == {
            "validities": [
                {
                    "name": "create",
                    "validity": {
                        "from": "2021-01-01T00:00:00+01:00",
                        "to": "2022-02-01T00:00:00+01:00",
                    },
                },
                {
                    "name": "update",
                    "validity": {
                        "from": "2022-02-02T00:00:00+01:00",
                        "to": "2024-04-04T00:00:00+02:00",
                    },
                },
            ]
        }
    else:
        # In GraphQL v29 they are the same dates as the ones we updated with,
        # as expected by any sane developer (and person, really).
        assert read == {
            "validities": [
                {
                    "name": "create",
                    "validity": {
                        "from": "2021-01-01T00:00:00+01:00",
                        "to": "2022-02-02T00:00:00+01:00",
                    },
                },
                {
                    "name": "update",
                    "validity": {
                        "from": "2022-02-02T00:00:00+01:00",
                        "to": "2024-04-04T00:00:00+02:00",
                    },
                },
            ]
        }

    validities = await read_sql()
    if version == Version.VERSION_28:
        # Once again, GraphQL v28 is lying
        assert validities == [
            # Create registration
            (
                "Aktiv",
                datetime(2021, 1, 1, 0, 0, tzinfo=DEFAULT_TIMEZONE),
                datetime(2023, 3, 4, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            ),
            # Update registration
            (
                "Aktiv",
                datetime(2022, 2, 2, 0, 0, tzinfo=DEFAULT_TIMEZONE),
                datetime(2024, 4, 5, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            ),
            (
                "Aktiv",
                datetime(2021, 1, 1, 0, 0, tzinfo=DEFAULT_TIMEZONE),
                datetime(2022, 2, 2, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            ),
        ]
    else:
        # But in v29, all datetimes are exactly the same as the ones we passed
        # to the GraphQL mutations.
        assert validities == [
            # Create registration
            (
                "Aktiv",
                datetime(2021, 1, 1, 0, 0, tzinfo=DEFAULT_TIMEZONE),
                datetime(2023, 3, 3, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            ),
            # Update registration
            (
                "Aktiv",
                datetime(2022, 2, 2, 0, 0, tzinfo=DEFAULT_TIMEZONE),
                datetime(2024, 4, 4, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            ),
            (
                "Aktiv",
                datetime(2021, 1, 1, 0, 0, tzinfo=DEFAULT_TIMEZONE),
                datetime(2022, 2, 2, 0, 0, tzinfo=DEFAULT_TIMEZONE),
            ),
        ]

    # Terminate
    graphapi_post(
        """
        mutation TerminateOrgUnit($input: OrganisationUnitTerminateInput!) {
          org_unit_terminate(input: $input) {
            uuid
          }
        }
        """,
        variables={
            "input": {
                "uuid": uuid,
                "from": "2021-12-12T00:00:00+01:00",
                "to": "2022-12-12T00:00:00+01:00",
            }
        },
        url=graphql_url,
    )

    read = await read_graphql()
    if version == Version.VERSION_28:
        # We have terminated the object from 2021-12-12 at midnight until
        # 2022-12-12 at midnight, so we would expect the object to be
        # terminated in between those dates *and times*, but that's not what
        # happens; we're off-by-one at *both* ends.
        assert read == {
            "validities": [
                {
                    "name": "create",
                    "validity": {
                        "from": "2021-01-01T00:00:00+01:00",
                        "to": "2021-12-11T00:00:00+01:00",
                    },
                },
                {
                    "name": "update",
                    "validity": {
                        "from": "2022-12-13T00:00:00+01:00",
                        "to": "2024-04-04T00:00:00+02:00",
                    },
                },
            ]
        }
    else:
        # Naturally, GraphQL v29 is sane 😎
        assert read == {
            "validities": [
                {
                    "name": "create",
                    "validity": {
                        "from": "2021-01-01T00:00:00+01:00",
                        "to": "2021-12-12T00:00:00+01:00",
                    },
                },
                {
                    "name": "update",
                    "validity": {
                        "from": "2022-12-12T00:00:00+01:00",
                        "to": "2024-04-04T00:00:00+02:00",
                    },
                },
            ]
        }

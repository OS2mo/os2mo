# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""How dates affect the engagement-related fields on an IT user.

An IT user has six engagement-related fields:

  - Raw (no resolver):  engagement_uuid, engagement_uuids, engagement_response
  - Resolver-backed:    engagement, engagements, engagements_responses

The raw fields read from the IT user's `tilknyttedefunktioner` effect at the
slice date and do no validity filtering of the engagement itself. The
resolver-backed fields take those UUIDs and pass them through
`engagement_resolver`, which filters by gyldighed/virkning.

These tests pin down how the IT user's slice date, the engagement resolver's
filter, and the absence of date propagation between the two interact.
"""
from collections.abc import Callable
from datetime import datetime
from datetime import timedelta
from typing import Any
from uuid import UUID

import pytest
from more_itertools import one

from tests.conftest import GraphAPIPost


_READ_ITUSER_ENGAGEMENT_FIELDS = """
    query ReadITUserEngagementFields(
      $uuid: UUID!,
      $start: DateTime,
      $end: DateTime,
      $engagement_filter: UuidsBoundEngagementFilter,
    ) {
      itusers(filter: {uuids: [$uuid]}) {
        objects {
          validities(start: $start, end: $end) {
            engagement_uuid
            engagement_uuids
            engagement(filter: $engagement_filter) { uuid }
            engagements(filter: $engagement_filter) { uuid }
            engagement_response { uuid }
            engagements_responses(filter: $engagement_filter) {
              objects { uuid }
            }
          }
        }
      }
    }
"""


@pytest.fixture
def outlived_engagement_ituser(
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> tuple[UUID, UUID]:
    """An IT user (open-ended) linked to an engagement that ended in 2021."""
    engagement_type_facet = create_facet(
        {"user_key": "engagement_type", "validity": {"from": "1900-01-01"}}
    )
    engagement_type = create_class(
        {
            "facet_uuid": str(engagement_type_facet),
            "user_key": "engagement_type_1",
            "name": "Engagement Type 1",
            "validity": {"from": "1900-01-01"},
        }
    )
    job_function_facet = create_facet(
        {"user_key": "job_function", "validity": {"from": "1900-01-01"}}
    )
    job_function = create_class(
        {
            "facet_uuid": str(job_function_facet),
            "user_key": "job_function_1",
            "name": "Job Function 1",
            "validity": {"from": "1900-01-01"},
        }
    )

    org_unit = create_org_unit("unit", None)
    person = create_person(None)
    itsystem = create_itsystem(
        {
            "user_key": "AD",
            "name": "Active Directory",
            "validity": {"from": "1900-01-01"},
        }
    )

    engagement = create_engagement(
        {
            "org_unit": str(org_unit),
            "person": str(person),
            "engagement_type": str(engagement_type),
            "job_function": str(job_function),
            "validity": {"from": "2020-01-01", "to": "2021-12-31"},
        }
    )

    ituser = create_ituser(
        {
            "user_key": "alice",
            "person": str(person),
            "itsystem": str(itsystem),
            "engagements": [str(engagement)],
            "validity": {"from": "2020-01-01"},
        }
    )
    return ituser, engagement


@pytest.fixture
def read_ituser_engagement_fields(
    graphapi_post: GraphAPIPost,
) -> Callable[..., dict[str, Any]]:
    """Read the six engagement-related fields on an IT user.

    Args:
        ituser_uuid: which IT user to read.
        ituser_at: slice date for the IT user's `validities`. The
            end of the range is automatically nudged by 1 ms because
            Postgres `tstzrange` canonicalises `[X, X)` as an empty
            range, which would match nothing. None means leave both
            start and end null (i.e. "all of time").
        engagement_filter: full `EngagementFilter` input passed verbatim
            to the resolver-backed fields (`engagement`, `engagements`,
            `engagements_responses`). None means no filter is applied
            and the resolver defaults to "now".

    The two are passed via independent GraphQL variables to show that
    they do not propagate into each other.
    """

    def inner(
        ituser_uuid: UUID,
        ituser_at: str | None = None,
        engagement_filter: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        start: str | None = None
        end: str | None = None
        if ituser_at is not None:
            start_dt = datetime.fromisoformat(ituser_at)
            start = start_dt.isoformat()
            end = (start_dt + timedelta(milliseconds=1)).isoformat()
        variables = {
            "uuid": str(ituser_uuid),
            "start": start,
            "end": end,
            "engagement_filter": engagement_filter,
        }
        response = graphapi_post(_READ_ITUSER_ENGAGEMENT_FIELDS, variables)
        assert response.errors is None
        return one(one(response.data["itusers"]["objects"])["validities"])

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_default_now_diverges(
    outlived_engagement_ituser: tuple[UUID, UUID],
    read_ituser_engagement_fields: Callable[..., dict[str, Any]],
) -> None:
    """Default lookup: IT user slice = all time, engagement filter = none.

    The engagement is no longer Aktiv at "now" (the resolver's default),
    so the resolver-backed fields are empty while the raw fields still
    surface the UUID.
    """
    ituser, engagement = outlived_engagement_ituser
    fields = read_ituser_engagement_fields(ituser)
    assert fields == {
        "engagement_uuid": str(engagement),
        "engagement_uuids": [str(engagement)],
        "engagement": [],
        "engagements": [],
        "engagement_response": {"uuid": str(engagement)},
        "engagements_responses": {"objects": []},
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_engagement_resolver_filter_scopes_lookup(
    outlived_engagement_ituser: tuple[UUID, UUID],
    read_ituser_engagement_fields: Callable[..., dict[str, Any]],
) -> None:
    """Passing an `EngagementFilter` scopes the engagement lookup to a
    date when the engagement was Aktiv, and all six fields agree."""
    ituser, engagement = outlived_engagement_ituser
    fields = read_ituser_engagement_fields(
        ituser, engagement_filter={"from_date": "2020-06-01"}
    )
    assert fields == {
        "engagement_uuid": str(engagement),
        "engagement_uuids": [str(engagement)],
        "engagement": [{"uuid": str(engagement)}],
        "engagements": [{"uuid": str(engagement)}],
        "engagement_response": {"uuid": str(engagement)},
        "engagements_responses": {"objects": [{"uuid": str(engagement)}]},
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_ituser_slice_does_not_propagate(
    outlived_engagement_ituser: tuple[UUID, UUID],
    read_ituser_engagement_fields: Callable[..., dict[str, Any]],
) -> None:
    """Sliding the IT user's `validities` window to a date when the
    engagement was active does NOT propagate to the nested engagement
    resolver. The resolver still defaults to "now", so the resolver-backed
    fields remain empty even though the IT user effect is read at
    2020-06-01."""
    ituser, engagement = outlived_engagement_ituser
    fields = read_ituser_engagement_fields(ituser, ituser_at="2020-06-01")
    assert fields == {
        "engagement_uuid": str(engagement),
        "engagement_uuids": [str(engagement)],
        "engagement": [],
        "engagements": [],
        "engagement_response": {"uuid": str(engagement)},
        "engagements_responses": {"objects": []},
    }

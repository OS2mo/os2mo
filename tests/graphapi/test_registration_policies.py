# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Reading the fields of registrations."""

from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from mora.graphapi.version import LATEST_VERSION
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

LATEST = f"/graphql/v{LATEST_VERSION.value}"
FIELDS = "uuid model registration_id start end actor note actor_object { uuid }"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "url,query,registrations",
    [
        # The legacy registrations, of every model
        (
            "/graphql/v25",
            f"query {{ registrations {{ objects {{ {FIELDS} }} }} }}",
            lambda data: data["registrations"]["objects"],
        ),
        # The registrations of a model
        (
            LATEST,
            f"""
            query {{
              registrations(filter: {{ models: ["employee"] }}) {{
                objects {{
                  {FIELDS}
                  ... on PersonRegistration {{ current {{ uuid }} validities {{ uuid }} }}
                }}
              }}
            }}
            """,
            lambda data: data["registrations"]["objects"],
        ),
        # The registrations of an object
        (
            LATEST,
            f"""
            query {{
              persons {{
                objects {{
                  registrations {{ {FIELDS} current {{ uuid }} validities {{ uuid }} }}
                }}
              }}
            }}
            """,
            lambda data: one(data["persons"]["objects"])["registrations"],
        ),
    ],
)
async def test_a_reader_reads_the_fields_of_registrations(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    create_person: Callable[[dict[str, Any] | None], UUID],
    url: str,
    query: str,
    registrations: Callable[[dict[str, Any]], list[dict[str, Any]]],
) -> None:
    """A reader reads every field of registrations."""
    person = create_person(None)
    set_auth({"reader"}, uuid4())

    response = graphapi_post(query, url=url)

    assert response.errors is None
    assert response.data
    assert one(registrations(response.data))["uuid"] == str(person)

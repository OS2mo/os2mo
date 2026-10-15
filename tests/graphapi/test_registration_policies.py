# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The fields of registrations are guarded by read policies."""

import json
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one
from sqlalchemy import func
from sqlalchemy import select

from mora.db import AsyncSession
from mora.db import BrugerRegistrering
from mora.db import Collection
from mora.db import FacetRegistrering
from mora.graphapi.version import LATEST_VERSION
from mora.mapping import ADMIN
from tests.conftest import ALVIDA_UUID
from tests.conftest import BRUCE_UUID
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import SetRules

DENIED = "No policy approved the access"
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
    """The seeded Reader policy grants a reader what the role used to."""
    person = create_person(None)
    set_auth({"reader"}, uuid4())

    response = graphapi_post(query, url=url)

    assert response.errors is None
    assert response.data
    assert one(registrations(response.data))["uuid"] == str(person)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "url,query,path",
    [
        # The legacy registrations, of every model, and of an object
        (
            "/graphql/v25",
            "query { registrations { objects { model actor } } }",
            ["registrations", "objects", 0, "actor"],
        ),
        (
            "/graphql/v26",
            "query { persons { objects { registrations { model actor } } } }",
            ["persons", "objects", 0, "registrations", 0, "actor"],
        ),
        # The registrations of every model, and of an object
        (
            LATEST,
            "query { registrations { objects { model actor } } }",
            ["registrations", "objects", 0, "actor"],
        ),
        (
            LATEST,
            "query { persons { objects { registrations { model actor } } } }",
            ["persons", "objects", 0, "registrations", 0, "actor"],
        ),
    ],
)
async def test_a_registration_field_no_rule_grants_is_denied(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    create_person: Callable[[dict[str, Any] | None], UUID],
    url: str,
    query: str,
    path: list[str | int],
) -> None:
    """A field of a registration no rule grants is denied where it is read."""
    create_person(None)
    await set_rules("policy_reader", Collection.Registration, {"model"})
    set_auth({"policy_reader"}, uuid4())

    response = graphapi_post(query, url=url)

    assert response.data is None
    error = one(response.errors)
    assert error["message"] == DENIED
    assert error["path"] == path


@pytest.mark.integration_test
async def test_a_rule_naming_one_model_grants_nothing_on_its_id_in_another_table(
    empty_db: AsyncSession,
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_facet: Callable[[dict[str, Any]], UUID],
) -> None:
    """A rule on the registrations of persons grants nothing on a facet's of the same id."""
    create_person(None)
    create_facet({"user_key": "facet", "validity": {"from": "2000-01-01"}})
    # Every registrering table numbers its registrations on its own
    person_id = one(await empty_db.scalars(select(BrugerRegistrering.id)))
    facet_id = one(await empty_db.scalars(select(FacetRegistrering.id)))
    assert person_id == facet_id
    await set_rules(
        "policy_reader",
        Collection.Registration,
        {"note"},
        condition='{"models": ["employee"]}',
    )
    set_auth({"policy_reader"}, uuid4())

    query = """
        query ($model: String!) {
          registrations(filter: { models: [$model] }) { objects { note } }
        }
    """
    person = graphapi_post(query, {"model": "employee"})
    facet = graphapi_post(query, {"model": "facet"})

    assert person.errors is None
    error = one(facet.errors)
    assert error["message"] == DENIED
    assert error["path"] == ["registrations", "objects", 0, "note"]


@pytest.mark.integration_test
async def test_a_rule_naming_an_actor_grants_nothing_on_another_registration_of_the_object(
    empty_db: AsyncSession,
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    set_rules: SetRules,
    create_person: Callable[[dict[str, Any] | None], UUID],
    update_person: Callable[[dict[str, Any]], UUID],
) -> None:
    """A registration is keyed by itself, rather than by the object it registers."""
    # Registered by the admin of the tests, then by another actor
    person = create_person(None)
    set_auth(ADMIN, ALVIDA_UUID)
    update_person(
        {
            "uuid": str(person),
            "given_name": "Alvida",
            "validity": {"from": "2000-01-01"},
        }
    )
    # As the registrations of the person are listed, by the time they were made
    registered = (
        select(BrugerRegistrering.actor)
        .select_from(BrugerRegistrering)
        .order_by(func.lower(BrugerRegistrering.registrering_period))
    )
    assert list(await empty_db.scalars(registered)) == [BRUCE_UUID, ALVIDA_UUID]
    await set_rules(
        "policy_reader",
        Collection.Registration,
        {"note"},
        condition=json.dumps({"actors": [str(ALVIDA_UUID)]}),
    )
    set_auth({"policy_reader"}, uuid4())

    response = graphapi_post("query { persons { objects { registrations { note } } } }")

    error = one(response.errors)
    assert error["message"] == DENIED
    assert error["path"] == ["persons", "objects", 0, "registrations", 0, "note"]

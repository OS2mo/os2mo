# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "binding_type_input, expected",
    [
        # Explicit value on create -> same value on read.
        ({"binding_type": "explicit"}, "explicit"),
        ({"binding_type": "implicit"}, "implicit"),
        # Field omitted from input -> null on read.
        ({}, None),
        # Explicit null on create -> null on read.
        ({"binding_type": None}, None),
        # Explicit "" on create -> null on read.
        ({"binding_type": ""}, None),
    ],
)
def test_it_user_binding_type_round_trip(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    binding_type_input: dict[str, Any],
    expected: str | None,
) -> None:
    """Creating an IT-user stores binding_type and reads it back as expected."""
    itsystem_uuid = create_itsystem(
        {
            "user_key": "AD",
            "name": "Active Directory",
            "validity": {"from": "2024-01-01"},
        }
    )
    person_uuid = create_person({"given_name": "Ada", "surname": "Lovelace"})
    ituser_uuid = create_ituser(
        {
            "user_key": "ada",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "validity": {"from": "2024-01-01"},
            **binding_type_input,
        }
    )

    read_query = """
        query Read($uuid: UUID!) {
            itusers(filter: {uuids: [$uuid]}) {
                objects {
                    validities {
                        binding_type
                    }
                }
            }
        }
    """
    response = graphapi_post(read_query, {"uuid": str(ituser_uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["itusers"]["objects"])
    assert obj["validities"] == [{"binding_type": expected}]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "update_binding_type_input, expected_validities",
    [
        # New explicit value -> creates a second validity with the new value.
        (
            {"binding_type": "explicit"},
            [
                {
                    "binding_type": "initial",
                    "validity": {
                        "from": "2024-01-01T00:00:00+01:00",
                        "to": "2025-01-01T00:00:00+01:00",
                    },
                },
                {
                    "binding_type": "explicit",
                    "validity": {
                        "from": "2025-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ],
        ),
        # New implicit value -> creates a second validity with the new value.
        (
            {"binding_type": "implicit"},
            [
                {
                    "binding_type": "initial",
                    "validity": {
                        "from": "2024-01-01T00:00:00+01:00",
                        "to": "2025-01-01T00:00:00+01:00",
                    },
                },
                {
                    "binding_type": "implicit",
                    "validity": {
                        "from": "2025-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ],
        ),
        # Field omitted on update -> no binding_type change.
        (
            {},
            [
                {
                    "binding_type": "initial",
                    "validity": {
                        "from": "2024-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ],
        ),
        # Explicit null on update -> field filtered out -> no binding_type change.
        (
            {"binding_type": None},
            [
                {
                    "binding_type": "initial",
                    "validity": {
                        "from": "2024-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ],
        ),
        # Explicit "" on update -> creates a second validity with null.
        (
            {"binding_type": ""},
            [
                {
                    "binding_type": "initial",
                    "validity": {
                        "from": "2024-01-01T00:00:00+01:00",
                        "to": "2025-01-01T00:00:00+01:00",
                    },
                },
                {
                    "binding_type": None,
                    "validity": {
                        "from": "2025-01-01T00:00:00+01:00",
                        "to": None,
                    },
                },
            ],
        ),
    ],
)
def test_it_user_binding_type_update(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    update_binding_type_input: dict[str, Any],
    expected_validities: list[dict[str, Any]],
) -> None:
    """Updating binding_type creates a new validity reflecting the new value."""
    itsystem_uuid = create_itsystem(
        {
            "user_key": "AD",
            "name": "Active Directory",
            "validity": {"from": "2024-01-01"},
        }
    )
    person_uuid = create_person({"given_name": "Alan", "surname": "Turing"})
    ituser_uuid = create_ituser(
        {
            "user_key": "alan",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "binding_type": "initial",
            "validity": {"from": "2024-01-01"},
        }
    )

    update_response = graphapi_post(
        """
            mutation Update($input: ITUserUpdateInput!) {
                ituser_update(input: $input) {
                    uuid
                }
            }
        """,
        variables={
            "input": {
                "uuid": str(ituser_uuid),
                "validity": {"from": "2025-01-01"},
                **update_binding_type_input,
            }
        },
    )
    assert update_response.errors is None

    read_query = """
        query Read($uuid: UUID!) {
            itusers(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    validities(start: null, end: null) {
                        binding_type
                        validity {from to}
                    }
                }
            }
        }
    """
    response = graphapi_post(read_query, {"uuid": str(ituser_uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["itusers"]["objects"])
    assert obj["validities"] == expected_validities


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter, expected_keys",
    [
        # No filter -> all four returned.
        ({}, {"explicit", "implicit", "other", "unset"}),
        # Single binding_type -> just the matching user.
        ({"binding_types": ["explicit"]}, {"explicit"}),
        ({"binding_types": ["implicit"]}, {"implicit"}),
        # Multiple values OR-combine within the filter.
        ({"binding_types": ["explicit", "implicit"]}, {"explicit", "implicit"}),
        # Unknown value -> empty result.
        ({"binding_types": ["nonexistent"]}, set()),
        # Empty list -> empty result (no value matches the empty set).
        ({"binding_types": []}, set()),
        # Combined with user_keys -> AND-combine across filter fields.
        (
            {
                "user_keys": ["linus.explicit"],
                "binding_types": ["explicit"],
            },
            {"explicit"},
        ),
        # user_key matches but binding_type doesn't -> no result.
        (
            {
                "user_keys": ["linus.explicit"],
                "binding_types": ["implicit"],
            },
            set(),
        ),
        # binding_type narrows a multi-user_keys match.
        (
            {
                "user_keys": ["linus.explicit", "linus.implicit"],
                "binding_types": ["implicit"],
            },
            {"implicit"},
        ),
    ],
)
def test_it_user_binding_type_filter(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    filter: dict[str, Any],
    expected_keys: set[str],
) -> None:
    """IT-users can be filtered by binding_type."""
    itsystem_uuid = create_itsystem(
        {
            "user_key": "AD",
            "name": "Active Directory",
            "validity": {"from": "2024-01-01"},
        }
    )
    person_uuid = create_person({"given_name": "Linus", "surname": "Torvalds"})

    def make(user_key: str, **extra: Any) -> UUID:
        return create_ituser(
            {
                "user_key": user_key,
                "itsystem": str(itsystem_uuid),
                "person": str(person_uuid),
                "validity": {"from": "2024-01-01"},
                **extra,
            }
        )

    itusers = {
        "explicit": make("linus.explicit", binding_type="explicit"),
        "implicit": make("linus.implicit", binding_type="implicit"),
        "other": make("linus.other", binding_type="other"),
        "unset": make("linus.unset"),
    }

    query = """
        query Read($filter: ITUserFilter) {
            itusers(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(query, {"filter": filter})
    assert response.errors is None
    assert response.data
    actual = {UUID(o["uuid"]) for o in response.data["itusers"]["objects"]}
    assert actual == {itusers[k] for k in expected_keys}


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "update, expected_new_validity",
    [
        # Update binding_type only -> external_id preserved.
        (
            {"binding_type": "bt-2", "validity": {"from": "2025-01-01"}},
            {"external_id": "ext-1", "binding_type": "bt-2"},
        ),
        # Update external_id only -> binding_type preserved.
        (
            {"external_id": "ext-2", "validity": {"from": "2025-01-01"}},
            {"external_id": "ext-2", "binding_type": "bt-1"},
        ),
        # Update both at once.
        (
            {
                "external_id": "ext-2",
                "binding_type": "bt-2",
                "validity": {"from": "2025-01-01"},
            },
            {"external_id": "ext-2", "binding_type": "bt-2"},
        ),
    ],
)
def test_it_user_extension_update(
    graphapi_post: GraphAPIPost,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    update: dict[str, Any],
    expected_new_validity: dict[str, str],
) -> None:
    """Partial and full updates to the udvidelser-backed extensions
    (external_id, binding_type) produce a new validity reflecting only the
    fields that were updated; the untouched extension is preserved.
    """
    itsystem_uuid = create_itsystem(
        {
            "user_key": "AD",
            "name": "Active Directory",
            "validity": {"from": "2024-01-01"},
        }
    )
    person_uuid = create_person({"given_name": "Donald", "surname": "Knuth"})
    ituser_uuid = create_ituser(
        {
            "user_key": "knuth",
            "itsystem": str(itsystem_uuid),
            "person": str(person_uuid),
            "external_id": "ext-1",
            "binding_type": "bt-1",
            "validity": {"from": "2024-01-01"},
        }
    )

    update_response = graphapi_post(
        """
            mutation Update($input: ITUserUpdateInput!) {
                ituser_update(input: $input) {
                    uuid
                }
            }
        """,
        variables={"input": {"uuid": str(ituser_uuid), **update}},
    )
    assert update_response.errors is None

    read_query = """
        query Read($uuid: UUID!) {
            itusers(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    validities(start: null, end: null) {
                        external_id
                        binding_type
                        validity {from to}
                    }
                }
            }
        }
    """
    response = graphapi_post(read_query, {"uuid": str(ituser_uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["itusers"]["objects"])
    assert obj["validities"] == [
        {
            "external_id": "ext-1",
            "binding_type": "bt-1",
            "validity": {
                "from": "2024-01-01T00:00:00+01:00",
                "to": "2025-01-01T00:00:00+01:00",
            },
        },
        {
            **expected_new_validity,
            "validity": {"from": "2025-01-01T00:00:00+01:00", "to": None},
        },
    ]

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder

from mora.mapping import ADMIN
from mora.mapping import OWNER
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied
from tests.conftest import assert_granted

# IT systems; the envvar below names it, so the test must create that very one
ACTIVE_DIRECTORY = "c6a1d6f4-1e0b-4a4e-9d59-7f3b2a8e5c10"


@pytest.fixture
def users(alice: UUID, bob: UUID) -> dict[str | None, UUID | None]:
    """The users the tokens name: Alice owns HUM, Bob owns nothing."""
    return {None: None, "alice": alice, "bob": bob}


@pytest.fixture
def units(
    create_org_unit: Callable[..., UUID],
    make_owner: Callable[..., None],
    alice: UUID,
) -> dict[str, UUID]:
    """A root with HUM and SOCIAL below it, and FILOSOFISK below HUM.

    Alice owns HUM, and through it FILOSOFISK.
    """
    root = create_org_unit("root")
    hum = create_org_unit("hum", root)
    filosofisk = create_org_unit("filosofisk", hum)
    social = create_org_unit("social", root)
    make_owner(alice, org_unit=hum)
    return {"root": root, "hum": hum, "filosofisk": filosofisk, "social": social}


@pytest.fixture
def address_type_facet(create_facet: Callable[[dict[str, Any]], UUID]) -> UUID:
    return create_facet(
        {"user_key": "org_unit_address_type", "validity": {"from": "1970-01-01"}}
    )


@pytest.fixture
def phone_type(
    create_class: Callable[[dict[str, Any]], UUID], address_type_facet: UUID
) -> UUID:
    return create_class(
        {
            "user_key": "phone",
            "name": "Telefon",
            "scope": "PHONE",
            "facet_uuid": str(address_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )


@pytest.fixture
def dar_type(
    create_class: Callable[[dict[str, Any]], UUID], address_type_facet: UUID
) -> UUID:
    return create_class(
        {
            "user_key": "dar",
            "name": "Adresse",
            "scope": "DAR",
            "facet_uuid": str(address_type_facet),
            "validity": {"from": "1970-01-01"},
        }
    )


@pytest.fixture
def my_unit() -> UUID:
    # The unit the tests create themselves
    return uuid4()


@pytest.fixture
def org_unit_create_input(my_unit: UUID, units: dict[str, UUID]) -> dict[str, Any]:
    return {
        "uuid": my_unit,
        "name": "Fake Corp",
        "parent": units["root"],
        "org_unit_type": uuid4(),
        "org_unit_hierarchy": uuid4(),
        "org_unit_level": uuid4(),
        "time_planning": uuid4(),
        "validity": {"from": "2016-02-04", "to": None},
    }


@pytest.fixture
def address_create_phone_input(my_unit: UUID, phone_type: UUID) -> dict[str, Any]:
    return {
        "address_type": phone_type,
        "org_unit": my_unit,
        "validity": {"from": "2016-02-04"},
        "value": "11223344",
    }


@pytest.fixture
def address_create_dar_input(my_unit: UUID, dar_type: UUID) -> dict[str, Any]:
    return {
        "address_type": dar_type,
        "org_unit": my_unit,
        "validity": {"from": "2016-02-04"},
        # Aabogade 15, a real DAR address
        "value": "44c532e1-f617-4174-b144-d37ce9fda2bd",
    }


@pytest.fixture
def hum_address(
    create_address: Callable[[dict[str, Any]], UUID],
    units: dict[str, UUID],
    phone_type: UUID,
) -> UUID:
    # A phone number on HUM
    return create_address(
        {
            "address_type": str(phone_type),
            "org_unit": str(units["hum"]),
            "validity": {"from": "2016-01-01"},
            "value": "87150000",
        }
    )


@pytest.fixture
def hum_association(
    create_association: Callable[[dict[str, Any]], UUID],
    units: dict[str, UUID],
    alice: UUID,
) -> UUID:
    # Alice's own association with HUM
    return create_association(
        {
            "org_unit": str(units["hum"]),
            "person": str(alice),
            "association_type": str(uuid4()),
            "validity": {"from": "2017-01-01"},
        }
    )


@pytest.fixture
def hum_manager(
    create_manager: Callable[..., UUID],
    units: dict[str, UUID],
    alice: UUID,
) -> UUID:
    # Alice as the manager of HUM
    return create_manager(units["hum"], alice, validity={"from": "2017-01-01"})


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, user, success",
    [
        (None, None, False),
        (OWNER, "alice", False),
        (ADMIN, "alice", True),
    ],
)
def test_create_org_unit(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    users: dict[str | None, UUID | None],
    org_unit_create_input: dict[str, Any],
    address_create_phone_input: dict[str, Any],
    address_create_dar_input: dict[str, Any],
    role: str,
    user: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the admin role
    """
    set_auth(role, users[user])

    r1 = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=org_unit_create_input)),
    )
    r2 = graphapi_post(
        """
          mutation AddressCreate($input: AddressCreateInput!) {
            address_create(input: $input) {
              uuid
            }
          }
        """,
        variables=jsonable_encoder(dict(input=address_create_phone_input)),
    )
    r3 = graphapi_post(
        """
          mutation AddressCreate($input: AddressCreateInput!) {
            address_create(input: $input) {
              uuid
            }
          }
        """,
        variables=jsonable_encoder(dict(input=address_create_dar_input)),
    )
    for r in (r1, r2, r3):
        if success:
            assert_granted(r)
        else:
            assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_success_when_creating_unit_as_owner_of_parent_unit(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    alice: UUID,
    units: dict[str, UUID],
    org_unit_create_input: dict[str, Any],
) -> None:
    set_auth(OWNER, alice)

    input = {
        **org_unit_create_input,
        "parent": units["hum"],
    }
    r = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    assert_granted(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, user, success",
    [
        (None, None, False),
        (OWNER, "alice", False),
        (ADMIN, "alice", True),
    ],
)
def test_create_top_level_unit(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    users: dict[str | None, UUID | None],
    org_unit_create_input: dict[str, Any],
    role: str,
    user: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role
    3) User with the admin role
    """
    set_auth(role, users[user])

    input = {
        **org_unit_create_input,
        "parent": None,
    }
    r = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, user, success",
    [
        (None, None, False),
        (OWNER, "bob", False),
        (OWNER, "alice", True),
        (ADMIN, "bob", True),
    ],
)
def test_rename_org_unit(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    users: dict[str | None, UUID | None],
    units: dict[str, UUID],
    role: str,
    user: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role
    """
    set_auth(role, users[user])

    # Payload for renaming HUM, repeating the parent it already has
    input = {
        "uuid": units["hum"],
        "name": "New name",
        "parent": units["root"],
        "validity": {"from": "2021-07-28"},
    }

    r = graphapi_post(
        """
        mutation OrgUnitUpdate($input: OrganisationUnitUpdateInput!) {
          org_unit_update(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.fixture
def org_unit_no_details_uuid(
    create_org_unit: Callable[..., UUID],
    org_unit_uuid_1: UUID,
) -> UUID:
    return create_org_unit("no-details", org_unit_uuid_1)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, user, success",
    [
        (None, None, False),
        (OWNER, "bob", False),
        (OWNER, "alice", True),
        (ADMIN, "bob", True),
    ],
)
def test_terminate_org_unit(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    users: dict[str | None, UUID | None],
    org_unit_no_details_uuid: UUID,
    role: str,
    user: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role
    """
    set_auth(role, users[user])

    # Payload for terminating the newly created org unit
    terminate = {
        "uuid": org_unit_no_details_uuid,
        "to": datetime.today().strftime("%Y-%m-%d"),
    }
    r = graphapi_post(
        """
        mutation OrgUnitTerminate($input: OrganisationUnitTerminateInput!) {
          org_unit_terminate(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=terminate)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, user, success",
    [
        (None, None, False),
        (OWNER, "bob", False),
        (OWNER, "alice", True),
        (ADMIN, "bob", True),
    ],
)
def test_create_detail(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    users: dict[str | None, UUID | None],
    units: dict[str, UUID],
    org_unit_create_input: dict[str, Any],
    address_create_phone_input: dict[str, Any],
    role: str,
    user: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role
    """
    set_auth(ADMIN, users["alice"])
    r1 = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=org_unit_create_input)),
    )
    assert_granted(r1)

    set_auth(role, users[user])
    input = {
        **address_create_phone_input,
        "org_unit": units["hum"],
    }
    r2 = graphapi_post(
        """
          mutation AddressCreate($input: AddressCreateInput!) {
            address_create(input: $input) {
              uuid
            }
          }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r2)
    else:
        assert_denied(r2)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, user, success",
    [
        (None, None, False),
        (OWNER, "bob", False),
        (OWNER, "alice", True),
        (ADMIN, "bob", True),
    ],
)
def test_edit_detail(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    users: dict[str | None, UUID | None],
    units: dict[str, UUID],
    phone_type: UUID,
    hum_address: UUID,
    role: str,
    user: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role
    """
    set_auth(role, users[user])

    # Payload for editing detail (phone number) on org unit (hum)
    input = {
        "uuid": hum_address,
        "address_type": phone_type,
        "org_unit": units["hum"],
        "validity": {"from": "2016-01-01"},
        "value": "00000000",
    }
    r = graphapi_post(
        """
        mutation AddressUpdate($input: AddressUpdateInput!) {
          address_update(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, user, success",
    [
        (OWNER, "alice", True),
        (OWNER, "bob", False),
    ],
)
def test_rename_subunit(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    users: dict[str | None, UUID | None],
    org_unit_uuid_2: UUID,
    role: str,
    user: str,
    success: bool,
) -> None:
    """
    Test that an org unit can be modified by a user who owns the parent
    unit but not the unit subject to modification itself.
    """
    set_auth(role, users[user])

    input = {
        "uuid": org_unit_uuid_2,
        "name": "New name",
        "validity": {"from": "2021-07-28"},
    }
    r = graphapi_post(
        """
        mutation OrgUnitUpdate($input: OrganisationUnitUpdateInput!) {
          org_unit_update(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.fixture
def org_unit_uuid_1(
    create_org_unit: Callable[..., UUID],
    make_owner: Callable[..., None],
    units: dict[str, UUID],
    alice: UUID,
) -> UUID:
    # A unit below the root, owned by Alice
    org_uuid = create_org_unit("unit-1", units["root"])
    make_owner(alice, org_unit=org_uuid)
    return org_uuid


@pytest.fixture
def org_unit_uuid_2(
    create_org_unit: Callable[..., UUID],
    org_unit_uuid_1: UUID,
) -> UUID:
    return create_org_unit("unit-2", org_unit_uuid_1)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "owner,unit,one_is_parent,success",
    [
        # test_owner_of_unit_moves_unit_to_owned_unit
        ("alice", "hum", True, True),
        # test_owner_of_unit_moves_unit_to_subunit_of_owned_unit
        ("alice", "hum", False, True),
        # test_non_owner_of_unit_moves_unit_to_non_owned_unit
        ("bob", "hum", True, False),
        # test_non_owner_of_unit_moves_unit_to_subunit_of_non_owned_unit
        ("bob", "hum", False, False),
        # test_owner_moves_owned_subunit_to_owned_subunit
        ("alice", "filosofisk", False, True),
    ],
)
def test_owner_of_unit(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    users: dict[str | None, UUID | None],
    units: dict[str, UUID],
    org_unit_uuid_1: UUID,
    org_unit_uuid_2: UUID,
    owner: str,
    unit: str,
    one_is_parent: bool,
    success: bool,
) -> None:
    # Alice owns both parent units, Bob neither
    set_auth(OWNER, users[owner])

    parent_uuid = org_unit_uuid_1 if one_is_parent else org_unit_uuid_2

    input = {
        "uuid": units[unit],
        "parent": parent_uuid,
        "validity": {"from": "2021-07-30"},
    }
    r = graphapi_post(
        """
        mutation OrgUnitUpdate($input: OrganisationUnitUpdateInput!) {
          org_unit_update(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "origin,destinations,success",
    [
        # owner of origin and owner of all destinations
        ("hum", ["filosofisk"], True),
        # owner of origin but not owner of all destinations
        ("hum", ["filosofisk", "root"], True),
        # not owner of origin but owner of all destinations
        ("root", ["filosofisk"], False),
        # not owner of origin and not owner of all destinations
        ("root", ["social"], False),
    ],
)
def test_related(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    alice: UUID,
    units: dict[str, UUID],
    origin: str,
    destinations: list[str],
    success: bool,
) -> None:
    set_auth(OWNER, alice)
    input = {
        "origin": units[origin],
        "destination": [units[d] for d in destinations],
        "validity": {"from": "2020-01-01"},
    }
    r = graphapi_post(
        """
        mutation RelateUnits($input: RelatedUnitsUpdateInput!) {
          related_units_update(input: $input) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize("detail", ["address", "association", "manager"])
def test_terminate_x_as_owner_of_unit(
    request: pytest.FixtureRequest,
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    alice: UUID,
    detail: str,
) -> None:
    # Each detail sits on HUM, which Alice owns
    uuid = request.getfixturevalue(f"hum_{detail}")
    set_auth(OWNER, alice)
    r = graphapi_post(
        f"""
        mutation Terminate($uuid: UUID!) {{
          {detail}_terminate(input: {{ uuid: $uuid, to: "2021-07-16" }}) {{
            uuid
          }}
        }}
        """,
        variables=jsonable_encoder({"uuid": uuid}),
    )
    assert_granted(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "token,success",
    [
        ("user_key", False),
        ("external_id", True),
        ("person", False),
    ],
)
@pytest.mark.envvar(
    {"KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS": ACTIVE_DIRECTORY}
)
def test_ownership_through_it_system(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    alice: UUID,
    hum_address: UUID,
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
    token: str,
    success: bool,
) -> None:
    # Alice, who owns HUM, has a user in the authoritative IT system. Both its
    # user_key and its external_id look like the uuid a token carries, but only
    # the external_id identifies her
    user_key = str(uuid4())
    external_id = str(uuid4())
    create_itsystem(
        {
            "uuid": ACTIVE_DIRECTORY,
            "user_key": "Active Directory",
            "name": "Active Directory",
            "validity": {"from": "1970-01-01"},
        }
    )
    create_ituser(
        {
            "user_key": user_key,
            "external_id": external_id,
            "itsystem": ACTIVE_DIRECTORY,
            "person": str(alice),
            "validity": {"from": "2017-01-01"},
        }
    )
    tokens = {
        "user_key": user_key,
        "external_id": external_id,
        "person": alice,
    }
    set_auth(OWNER, tokens[token])

    r = graphapi_post(
        """
        mutation Terminate($uuid: UUID!) {
          address_terminate(input: { uuid: $uuid, to: "2021-07-16" }) {
            uuid
          }
        }
        """,
        variables=jsonable_encoder({"uuid": hum_address}),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)

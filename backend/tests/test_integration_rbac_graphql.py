# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from mora.auth.exceptions import AuthorizationError
from mora.auth.keycloak.rbac import _get_employee_uuid_via_it_system
from mora.config import Settings
from mora.mapping import ADMIN
from mora.mapping import OWNER

from tests import util
from tests.conftest import GraphAPIPost

# Users
ANDERS_AND = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
FEDTMULE = "6ee24785-ee9a-4502-81c2-7697009c9053"

# Org units
MY_UNIT = "9de978da-0967-43cf-921d-d56ddfcc6e0e"
ROOT_UNIT = "2874e1dc-85e6-4269-823a-e1125484dfd3"
HUM_UNIT = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
FILOSOFISK_INSTITUT = "85715fc7-925d-401b-822d-467eb4b163b6"
SOCIAL_OG_SUNDHED = "68c5d78e-ae26-441f-a143-0103eca8b62a"

# IT systems
ACTIVE_DIRECTORY = UUID("59c135c9-2b15-41cc-97c8-b5dff7180beb")

# IT users
ANDERS_AND_AD_USER = "18d2271a-45c4-406c-a482-04ab12f80881"


@pytest.fixture(autouse=True)
def enable_rbac(set_settings: Callable[..., None]) -> None:
    """Configure settings as required to enable GraphQL RBAC."""
    set_settings(
        **{
            "os2mo_auth": "True",
            "keycloak_rbac_enabled": "True",
            "graphql_rbac": "True",
        }
    )


@pytest.fixture
def org_unit_create_input() -> dict[str, Any]:
    return {
        "uuid": MY_UNIT,
        "name": "Fake Corp",
        "parent": ROOT_UNIT,
        "org_unit_type": "ca76a441-6226-404f-88a9-31e02e420e52",
        "org_unit_hierarchy": "12345678-abcd-abcd-1234-12345678abcd",
        "org_unit_level": "0f015b67-f250-43bb-9160-043ec19fad48",
        "time_planning": "ca76a441-6226-404f-88a9-31e02e420e52",
        "validity": {"from": "2016-02-04", "to": None},
    }


@pytest.fixture
def address_create_phone_input() -> dict[str, Any]:
    return {
        "address_type": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
        "org_unit": MY_UNIT,
        "validity": {"from": "2016-02-04"},
        "value": "11223344",
    }


@pytest.fixture
def address_create_dar_input() -> dict[str, Any]:
    return {
        "address_type": "4e337d8e-1fd2-4449-8110-e0c8a22958ed",
        "org_unit": MY_UNIT,
        "validity": {"from": "2016-02-04"},
        "value": "44c532e1-f617-4174-b144-d37ce9fda2bd",
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, success",
    [
        (None, None, False),
        (OWNER, ANDERS_AND, False),
        (ADMIN, ANDERS_AND, True),
    ],
)
def test_create_org_unit(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_create_input: dict[str, Any],
    address_create_phone_input: dict[str, Any],
    address_create_dar_input: dict[str, Any],
    role: str,
    userid: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the admin role
    """
    set_auth(role, userid)

    r1 = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=org_unit_create_input),
    )
    r2 = graphapi_post(
        """
          mutation AddressCreate($input: AddressCreateInput!) {
            address_create(input: $input) {
              uuid
            }
          }
        """,
        variables=dict(input=address_create_phone_input),
    )
    r3 = graphapi_post(
        """
          mutation AddressCreate($input: AddressCreateInput!) {
            address_create(input: $input) {
              uuid
            }
          }
        """,
        variables=dict(input=address_create_dar_input),
    )
    if success:
        assert all(r.errors is None for r in (r1, r2, r3))
    else:
        assert any(r.errors is not None for r in (r1, r2, r3))


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_success_when_creating_unit_as_owner_of_parent_unit(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_create_input: dict[str, Any],
) -> None:
    set_auth(OWNER, ANDERS_AND)

    input = {
        **org_unit_create_input,
        "parent": HUM_UNIT,
    }
    r = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=input),
    )
    assert r.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, success",
    [
        (None, None, False),
        (OWNER, ANDERS_AND, False),
        (ADMIN, ANDERS_AND, True),
    ],
)
def test_create_top_level_unit(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_create_input: dict[str, Any],
    role: str,
    userid: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role
    3) User with the admin role
    """
    set_auth(role, userid)

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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, success",
    [
        (None, None, False),
        (OWNER, FEDTMULE, False),
        (OWNER, ANDERS_AND, True),
        (ADMIN, FEDTMULE, True),
    ],
)
def test_rename_org_unit(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role
    """
    set_auth(role, userid)

    # Payload for renaming Humanistisk Fakultet
    input = {
        "uuid": HUM_UNIT,
        "name": "New name",
        "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.fixture
def org_unit_no_details_uuid(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_create_input: dict[str, Any],
    org_unit_uuid_1: str,
) -> str:
    set_auth(ADMIN, FEDTMULE)

    input = {
        **org_unit_create_input,
        "uuid": str(uuid4()),
        "parent": org_unit_uuid_1,
    }
    r = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=input),
    )
    assert r.errors is None
    return r.data["org_unit_create"]["uuid"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, success",
    [
        (None, None, False),
        (OWNER, FEDTMULE, False),
        (OWNER, ANDERS_AND, True),
        (ADMIN, FEDTMULE, True),
    ],
)
def test_terminate_org_unit(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_no_details_uuid: str,
    role: str,
    userid: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role
    """
    set_auth(role, userid)

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
        variables=dict(input=terminate),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, success",
    [
        (None, None, False),
        (OWNER, FEDTMULE, False),
        (OWNER, ANDERS_AND, True),
        (ADMIN, FEDTMULE, True),
    ],
)
def test_create_detail(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_create_input: dict[str, Any],
    address_create_phone_input: dict[str, Any],
    role: str,
    userid: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role
    """
    set_auth(ADMIN, ANDERS_AND)
    r1 = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=org_unit_create_input),
    )
    assert r1.errors is None

    set_auth(role, userid)
    input = {
        **address_create_phone_input,
        "org_unit": HUM_UNIT,
    }
    r2 = graphapi_post(
        """
          mutation AddressCreate($input: AddressCreateInput!) {
            address_create(input: $input) {
              uuid
            }
          }
        """,
        variables=dict(input=input),
    )
    if success:
        assert r2.errors is None
    else:
        assert r2.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, success",
    [
        (None, None, False),
        (OWNER, FEDTMULE, False),
        (OWNER, ANDERS_AND, True),
        (ADMIN, FEDTMULE, True),
    ],
)
def test_edit_detail(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    """
    Test of write access for the following cases:
    1) Normal user (no roles set)
    2) User with the owner role, but not owner of the relevant entity
    3) User with the owner role and owner of the relative entity
    4) User with the admin role
    """
    set_auth(role, userid)

    # Payload for editing detail (phone number) on org unit (hum)
    input = {
        "uuid": "55848eca-4e9e-4f30-954b-78d55eec0473",
        "address_type": "1d1d3711-5af4-4084-99b3-df2b8752fdec",
        "org_unit": HUM_UNIT,
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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, success",
    [
        (OWNER, ANDERS_AND, True),
        (OWNER, FEDTMULE, False),
    ],
)
def test_rename_subunit(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_uuid_2: str,
    role: str,
    userid: str,
    success: bool,
) -> None:
    """
    Test that an org unit can be modified by a user who owns the parent
    unit but not the unit subject to modification itself.
    """
    set_auth(role, userid)

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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.fixture
def org_unit_uuid_1(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_create_input: dict[str, Any],
) -> str:
    set_auth(ADMIN, FEDTMULE)

    input = {
        **org_unit_create_input,
        "uuid": str(uuid4()),
    }
    r1 = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=input),
    )
    assert r1.errors is None
    org_uuid = r1.data["org_unit_create"]["uuid"]

    owner = {
        "owner": ANDERS_AND,
        "org_unit": org_uuid,
        "validity": {"from": "2021-08-03"},
    }
    r2 = graphapi_post(
        """
        mutation OwnerCreate($input: OwnerCreateInput!) {
          owner_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=owner),
    )
    assert r2.errors is None

    return org_uuid


@pytest.fixture
def org_unit_uuid_2(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_create_input: dict[str, Any],
    org_unit_uuid_1: str,
) -> str:
    set_auth(ADMIN, FEDTMULE)

    input = {
        **org_unit_create_input,
        "uuid": str(uuid4()),
        "parent": org_unit_uuid_1,
    }
    r = graphapi_post(
        """
        mutation OrgUnitCreate($input: OrganisationUnitCreateInput!) {
          org_unit_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=input),
    )
    assert r.errors is None
    return r.data["org_unit_create"]["uuid"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "owner,org_uuid,one_is_parent,success",
    [
        # test_owner_of_unit_moves_unit_to_owned_unit
        (ANDERS_AND, HUM_UNIT, True, True),
        # test_owner_of_unit_moves_unit_to_subunit_of_owned_unit
        (ANDERS_AND, HUM_UNIT, False, True),
        # test_non_owner_of_unit_moves_unit_to_non_owned_unit
        (FEDTMULE, HUM_UNIT, True, False),
        # test_non_owner_of_unit_moves_unit_to_subunit_of_non_owned_unit
        (FEDTMULE, HUM_UNIT, False, False),
        # test_owner_moves_owned_subunit_to_owned_subunit
        (ANDERS_AND, FILOSOFISK_INSTITUT, False, True),
    ],
)
def test_owner_of_unit(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    org_unit_uuid_1: str,
    org_unit_uuid_2: str,
    owner: str,
    org_uuid: str,
    one_is_parent: bool,
    success: bool,
) -> None:
    # Use user "Anders And" (who owns the parent unit)
    set_auth(OWNER, owner)

    parent_uuid = org_unit_uuid_1 if one_is_parent else org_unit_uuid_2

    input = {
        "uuid": org_uuid,
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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "origin,destinations,success",
    [
        # owner of origin and owner of all destinations
        (HUM_UNIT, [FILOSOFISK_INSTITUT], True),
        # owner of origin but not owner of all destinations
        (HUM_UNIT, [FILOSOFISK_INSTITUT, ROOT_UNIT], False),
        # not owner of origin but owner of all destinations
        (ROOT_UNIT, [FILOSOFISK_INSTITUT], False),
        # not owner of origin and not owner of all destinations
        (ROOT_UNIT, [SOCIAL_OG_SUNDHED], False),
    ],
)
def test_related(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    origin: str,
    destinations: list[str],
    success: bool,
) -> None:
    # We need a second org unit ANDERS_AND owns since we cannot relate an org unit with
    # itself; Make ANDERS_AND owner of FILOSOFISK_INSTITUT.
    set_auth(ADMIN, FEDTMULE)
    owner = {
        "owner": ANDERS_AND,
        "org_unit": FILOSOFISK_INSTITUT,
        "validity": {"from": "2020-01-01"},
    }
    r1 = graphapi_post(
        """
        mutation OwnerCreate($input: OwnerCreateInput!) {
          owner_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=owner),
    )
    assert r1.errors is None

    set_auth(OWNER, ANDERS_AND)
    input = {
        "origin": origin,
        "destination": destinations,
        "validity": {"from": "2020-01-01"},
    }
    r2 = graphapi_post(
        """
        mutation RelateUnits($input: RelatedUnitsUpdateInput!) {
          related_units_update(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=input),
    )
    if success:
        assert r2.errors is None
    else:
        assert r2.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "mutation",
    [
        'mutation Terminate {address_terminate(input: {uuid: "55848eca-4e9e-4f30-954b-78d55eec0473", to: "2021-07-16"}) {uuid}}',
        'mutation Terminate {association_terminate(input: {uuid: "c2153d5d-4a2b-492d-a18c-c498f7bb6221", to: "2021-07-16"}) {uuid}}',
        'mutation Terminate {manager_terminate(input: {uuid: "05609702-977f-4869-9fb4-50ad74c6999a", to: "2021-07-16"}) {uuid}}',
    ],
)
def test_terminate_x_as_owner_of_unit(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    mutation: str,
) -> None:
    set_auth(OWNER, ANDERS_AND)
    r = graphapi_post(mutation)
    assert r.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "token_uuid,success",
    [
        (ANDERS_AND_AD_USER, True),
        (ANDERS_AND, False),
    ],
)
@util.override_config(
    Settings(
        keycloak_rbac_authoritative_it_system_for_owners=ACTIVE_DIRECTORY,
    )
)
def test_ownership_through_it_system(
    set_auth: Callable[[str | None, str | None], None],
    graphapi_post: GraphAPIPost,
    token_uuid: str,
    success: bool,
) -> None:
    set_auth(OWNER, token_uuid)

    r = graphapi_post(
        """
        mutation Terminate {
          address_terminate(
            input: { uuid: "55848eca-4e9e-4f30-954b-78d55eec0473", to: "2021-07-16" }
          ) {
            uuid
          }
        }
        """,
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_it_user_to_employee_uuid():
    result = await _get_employee_uuid_via_it_system(
        ACTIVE_DIRECTORY, ANDERS_AND_AD_USER
    )
    assert ANDERS_AND == str(result)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_it_user_to_employee_uuid_missing_it_user():
    with pytest.raises(AuthorizationError):
        await _get_employee_uuid_via_it_system(ACTIVE_DIRECTORY, uuid4())

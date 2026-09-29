# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
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

# Users
ANDERS_AND = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
FEDTMULE = "6ee24785-ee9a-4502-81c2-7697009c9053"
LIS_JENSEN = "7626ad64-327d-481f-8b32-36c78eb12f8c"
ERIK_SMIDT_HANSEN = "236e0a78-11a0-4ed9-8545-6286bb8611c7"

Login = Callable[[str | None, str | None], None]


parametrize_roles = (
    "role, userid, success",
    # Test of write access for the following cases:
    [
        # 1) Normal user (no roles set)
        (None, None, False),
        # 2) User with the owner role, but not owner of the relevant entity
        (OWNER, "bob", False),
        # 3) User with the owner role and owner of the relative entity
        (OWNER, "alice", True),
        # 4) User with the admin role
        (ADMIN, "bob", True),
    ],
)


@pytest.fixture
def login(set_auth: SetAuth, alice: UUID, bob: UUID) -> Login:
    """Set the token of `role` for the user named by `userid`."""
    users = {"alice": alice, "bob": bob}

    def inner(role: str | None, userid: str | None) -> None:
        set_auth(role, users[userid] if userid is not None else None)

    return inner


@pytest.fixture
def sample_login(set_auth: SetAuth) -> Login:
    """Set the token of `role` for the user named by `userid`, in the sample
    data: Anders And plays Alice, the owner, and Fedtmule plays Bob."""
    users = {"alice": ANDERS_AND, "bob": FEDTMULE}

    def inner(role: str | None, userid: str | None) -> None:
        set_auth(role, users[userid] if userid is not None else None)

    return inner


@pytest.fixture
def carol(create_person: Callable[[dict[str, Any] | None], UUID]) -> UUID:
    return create_person({"given_name": "Carol", "surname": "Carlsen"})


@pytest.fixture
def unit(
    create_org_unit: Callable[..., UUID],
    alice: UUID,
    make_owner: Callable[..., None],
) -> UUID:
    """An org unit Alice owns."""
    unit = create_org_unit("unit")
    make_owner(alice, org_unit=unit)
    return unit


@pytest.fixture
def alice_owns_carol(alice: UUID, carol: UUID, make_owner: Callable[..., None]) -> None:
    make_owner(alice, person=carol)


@pytest.fixture
def alice_owns_bob(alice: UUID, bob: UUID, make_owner: Callable[..., None]) -> None:
    make_owner(alice, person=bob)


@pytest.fixture
def address_type(
    create_facet: Callable[[dict[str, Any]], UUID],
    create_class: Callable[[dict[str, Any]], UUID],
) -> Callable[[str], UUID]:
    """Create an employee address type of the given scope.

    Address mutators read the scope of the type to validate the value.
    """
    facet = create_facet(
        {"user_key": "employee_address_type", "validity": {"from": "1970-01-01"}}
    )

    def inner(scope: str) -> UUID:
        return create_class(
            {
                "facet_uuid": str(facet),
                "user_key": scope,
                "name": scope,
                "scope": scope,
                "validity": {"from": "1970-01-01"},
            }
        )

    return inner


@pytest.fixture
def phone_type(address_type: Callable[[str], UUID]) -> UUID:
    return address_type("PHONE")


@pytest.fixture
async def create_lis_owner(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
) -> None:
    # Let Anders And be the owner of Lis Jensen
    set_auth(ADMIN, ANDERS_AND)

    owner = {
        "owner": ANDERS_AND,
        "person": LIS_JENSEN,
        "validity": {"from": "2021-08-03"},
    }
    r = graphapi_post(
        """
        mutation OwnerCreate($input: OwnerCreateInput!) {
          owner_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=owner),
    )
    assert r.errors is None


@pytest.fixture
async def create_fedtmule_owner(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
) -> None:
    # Let Anders And be the owner of Fedtmule
    set_auth(ADMIN, ANDERS_AND)

    owner = {
        "owner": ANDERS_AND,
        "person": FEDTMULE,
        "validity": {"from": "2021-08-03"},
    }
    r = graphapi_post(
        """
        mutation OwnerCreate($input: OwnerCreateInput!) {
          owner_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=owner),
    )
    assert r.errors is None


@pytest.fixture
async def create_erik_owner(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
) -> None:
    # Let Anders And be the owner of Erik Smidt Hansen
    set_auth(ADMIN, ANDERS_AND)

    owner = {
        "owner": ANDERS_AND,
        "person": ERIK_SMIDT_HANSEN,
        "validity": {"from": "2021-08-03"},
    }
    r = graphapi_post(
        """
        mutation OwnerCreate($input: OwnerCreateInput!) {
          owner_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=owner),
    )
    assert r.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "role, userid, success",
    # Test of write access for the following cases:
    [
        # 1) Normal user (no roles set)
        (None, None, False),
        # 2) User with owner role
        (OWNER, "alice", False),
        # 3) User with the admin role
        (ADMIN, "alice", True),
    ],
)
def test_create_employee(
    login: Login,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)
    input = {
        "given_name": "Mickey",
        "surname": "Mouse",
        "nickname_given_name": "",
        "cpr_number": "1111111111",
    }
    r = graphapi_post(
        """
        mutation EmployeeCreate($input: EmployeeCreateInput!) {
          employee_create(input: $input) {
            uuid
          }
        }
        """,
        variables=dict(input=input),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "alice_owns_carol")
@pytest.mark.parametrize(*parametrize_roles)
def test_creating_detail_address(
    login: Login,
    graphapi_post: GraphAPIPost,
    phone_type: UUID,
    carol: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)

    # Payload for creating detail (phone number) on employee
    input = {
        "address_type": phone_type,
        "visibility": uuid4(),
        "employee": carol,
        "validity": {"from": "2021-08-04"},
        "value": "12345678",
    }
    r = graphapi_post(
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
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "alice_owns_carol")
def test_success_when_creating_it_system_detail_as_owner_of_employee(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    alice: UUID,
    carol: UUID,
    itsystem: UUID,
) -> None:
    # Use Alice (who owns the employee)
    set_auth(OWNER, alice)

    input = {
        "user_key": "AD",
        "person": carol,
        "itsystem": itsystem,
        "validity": {"from": "2021-08-11"},
    }
    r = graphapi_post(
        """
        mutation CreateITUser($input: ITUserCreateInput!){
            ituser_create(input: $input){
                uuid
            }
        }
        """,
        variables=jsonable_encoder(dict(input=input)),
    )
    assert_granted(r)


# When creating employee details in the frontend some details actually
# resides under an org unit, e.g. employment, role, association, ...
# A selection of these details are tested here (with respect to creating details)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "alice_owns_carol")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_employment(
    login: Login,
    graphapi_post: GraphAPIPost,
    carol: UUID,
    unit: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)

    input = {
        "person": carol,
        "org_unit": unit,
        "engagement_type": uuid4(),
        "job_function": uuid4(),
        "validity": {"from": "2021-08-11"},
    }
    r = graphapi_post(
        """
        mutation CreateEngagement($input: EngagementCreateInput!) {
          engagement_create(input: $input) {
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
@pytest.mark.usefixtures("empty_db", "alice_owns_bob")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_association(
    login: Login,
    graphapi_post: GraphAPIPost,
    carol: UUID,
    unit: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)

    input = {
        "person": carol,
        "org_unit": unit,
        "association_type": uuid4(),
        "validity": {"from": "2021-08-11"},
    }
    r = graphapi_post(
        """
        mutation CreateAssociation($input: AssociationCreateInput!) {
          association_create(input: $input) {
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
@pytest.mark.usefixtures("empty_db", "alice_owns_bob")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_manager(
    login: Login,
    graphapi_post: GraphAPIPost,
    carol: UUID,
    unit: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)

    input = {
        "person": carol,
        "org_unit": unit,
        "manager_type": uuid4(),
        "manager_level": uuid4(),
        "responsibility": uuid4(),
        "validity": {"from": "2021-08-11"},
    }
    r = graphapi_post(
        """
        mutation CreateManager($input: ManagerCreateInput!) {
          manager_create(input: $input) {
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
@pytest.mark.usefixtures("fixture_db", "create_erik_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_leave(
    sample_login: Login,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    sample_login(role, userid)

    input = {
        "person": ERIK_SMIDT_HANSEN,
        "leave_type": "bf65769c-5227-49b4-97c5-642cfbe41aa1",
        "engagement": "301a906b-ef51-4d5c-9c77-386fb8410459",
        "validity": {"from": "2021-08-20"},
    }
    r = graphapi_post(
        """
        mutation CreateLeave($input: LeaveCreateInput!) {
          leave_create(input: $input) {
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
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_edit_address(
    sample_login: Login,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    sample_login(role, userid)

    input = {
        "uuid": "64ea02e2-8469-4c54-a523-3d46729e86a7",
        "address_type": "c78eb6f7-8a9e-40b3-ac80-36b9f371c3e0",
        "visibility": "f63ad763-0e53-4972-a6a9-63b42a0f8cb7",
        "employee": FEDTMULE,
        "validity": {"from": "2021-08-13"},
        "value": "goofy@andeby.dk",
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
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_edit_association(
    sample_login: Login,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    sample_login(role, userid)

    input = {
        "uuid": "c2153d5d-4a2b-492d-a18c-c498f7bb6221",
        "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
        "association_type": "8eea787c-c2c7-46ca-bd84-2dd50f47801e",
        "employee": ANDERS_AND,
        "validity": {"from": "2021-08-25"},
    }
    r = graphapi_post(
        """
        mutation AssociationUpdate($input: AssociationUpdateInput!) {
          association_update(input: $input) {
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
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_edit_engagement(
    sample_login: Login,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    sample_login(role, userid)

    input = {
        "uuid": "301a906b-ef51-4d5c-9c77-386fb8410459",
        "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
        "job_function": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
        "engagement_type": "06f95678-166a-455a-a2ab-121a8d92ea23",
        "primary": "2f16d140-d743-4c9f-9e0e-361da91a06f6",
        "employee": ERIK_SMIDT_HANSEN,
        "validity": {"from": "2021-08-17"},
    }
    r = graphapi_post(
        """
        mutation EngagementUpdate($input: EngagementUpdateInput!) {
          engagement_update(input: $input) {
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
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_edit_manager(
    sample_login: Login,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    sample_login(role, userid)

    input = {
        "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
        "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
        "responsibility": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
        "manager_type": "0d72900a-22a4-4390-a01e-fd65d0e0999d",
        "manager_level": "991915c0-f4f4-4337-95fa-dbeb9da13247",
        "person": ANDERS_AND,
        "validity": {"from": "2021-08-25"},
    }
    r = graphapi_post(
        """
        mutation ManagerUpdate($input: ManagerUpdateInput!) {
          manager_update(input: $input) {
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
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(
    "mutation",
    [
        'mutation Terminate {address_terminate(input: {uuid: "64ea02e2-8469-4c54-a523-3d46729e86a7", to: "2021-08-20"}) {uuid}}',
        'mutation Terminate {engagement_terminate(input: {uuid: "301a906b-ef51-4d5c-9c77-386fb8410459", to: "2021-08-13"}) {uuid}}',
    ],
)
@pytest.mark.parametrize(*parametrize_roles)
def test_terminate_details(
    sample_login: Login,
    graphapi_post: GraphAPIPost,
    mutation: str,
    role: str,
    userid: str,
    success: bool,
) -> None:
    sample_login(role, userid)
    r = graphapi_post(mutation)
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_terminate_employee(
    sample_login: Login,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    sample_login(role, userid)
    input = {
        "uuid": LIS_JENSEN,
        "to": "2021-08-17",
    }
    r = graphapi_post(
        """
        mutation TerminateEmployee($input: EmployeeTerminateInput!) {
          employee_terminate(input: $input) {
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

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from string import Template
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
def bob_owns_alice(alice: UUID, bob: UUID, make_owner: Callable[..., None]) -> None:
    make_owner(bob, person=alice)


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
def email_type(address_type: Callable[[str], UUID]) -> UUID:
    return address_type("EMAIL")


@pytest.fixture
def email_address(
    email_type: UUID,
    create_address: Callable[[dict[str, Any]], UUID],
    bob: UUID,
) -> UUID:
    """An email address of Bob."""
    return create_address(
        {
            "address_type": str(email_type),
            "person": str(bob),
            "value": "bob@example.com",
            "validity": {"from": "2020-01-01"},
        }
    )


@pytest.fixture
def carols_engagement(
    create_engagement: Callable[[dict[str, Any]], UUID],
    carol: UUID,
    unit: UUID,
) -> UUID:
    """An engagement of Carol, in the unit Alice owns."""
    return create_engagement(
        {
            "person": str(carol),
            "org_unit": str(unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2020-01-01"},
        }
    )


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
@pytest.mark.usefixtures("empty_db", "alice_owns_carol")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_leave(
    login: Login,
    graphapi_post: GraphAPIPost,
    carol: UUID,
    carols_engagement: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)

    input = {
        "person": carol,
        "leave_type": uuid4(),
        "engagement": carols_engagement,
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
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "alice_owns_bob")
@pytest.mark.parametrize(*parametrize_roles)
def test_edit_address(
    login: Login,
    graphapi_post: GraphAPIPost,
    email_type: UUID,
    bob: UUID,
    email_address: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)

    input = {
        "uuid": email_address,
        "address_type": email_type,
        "visibility": uuid4(),
        "employee": bob,
        "validity": {"from": "2021-08-13"},
        "value": "bob.jensen@example.com",
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
@pytest.mark.usefixtures("empty_db", "alice_owns_bob", "bob_owns_alice")
@pytest.mark.parametrize(*parametrize_roles)
def test_edit_association(
    login: Login,
    graphapi_post: GraphAPIPost,
    create_association: Callable[[dict[str, Any]], UUID],
    alice: UUID,
    unit: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    # Alice's own association, in the unit she owns. Bob owns the association
    # through its person, Alice, but not the unit the update names, so that
    # unit is what denies him
    association = create_association(
        {
            "person": str(alice),
            "org_unit": str(unit),
            "association_type": str(uuid4()),
            "validity": {"from": "2020-01-01"},
        }
    )
    login(role, userid)

    input = {
        "uuid": association,
        "org_unit": unit,
        "association_type": uuid4(),
        "employee": alice,
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
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "alice_owns_bob")
@pytest.mark.parametrize(*parametrize_roles)
def test_edit_engagement(
    login: Login,
    graphapi_post: GraphAPIPost,
    carol: UUID,
    unit: UUID,
    carols_engagement: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)

    input = {
        "uuid": carols_engagement,
        "org_unit": unit,
        "job_function": uuid4(),
        "engagement_type": uuid4(),
        "primary": uuid4(),
        "employee": carol,
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
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "alice_owns_bob", "bob_owns_alice")
@pytest.mark.parametrize(*parametrize_roles)
def test_edit_manager(
    login: Login,
    graphapi_post: GraphAPIPost,
    create_manager: Callable[..., UUID],
    alice: UUID,
    unit: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    # Alice is herself the manager of the unit she owns. Bob owns the manager
    # through its person, Alice, but not the unit the update names, so that
    # unit is what denies him
    manager = create_manager(unit, alice, {"from": "2020-01-01"})
    login(role, userid)

    input = {
        "uuid": manager,
        "org_unit": unit,
        "responsibility": uuid4(),
        "manager_type": uuid4(),
        "manager_level": uuid4(),
        "person": alice,
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
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "alice_owns_bob")
@pytest.mark.parametrize(
    "mutation",
    [
        'mutation Terminate {address_terminate(input: {uuid: "$address", to: "2021-08-20"}) {uuid}}',
        'mutation Terminate {engagement_terminate(input: {uuid: "$engagement", to: "2021-08-13"}) {uuid}}',
    ],
)
@pytest.mark.parametrize(*parametrize_roles)
def test_terminate_details(
    login: Login,
    graphapi_post: GraphAPIPost,
    email_address: UUID,
    carols_engagement: UUID,
    mutation: str,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)
    r = graphapi_post(
        Template(mutation).substitute(
            address=email_address, engagement=carols_engagement
        )
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db", "alice_owns_carol")
@pytest.mark.parametrize(*parametrize_roles)
def test_terminate_employee(
    login: Login,
    graphapi_post: GraphAPIPost,
    carol: UUID,
    role: str,
    userid: str,
    success: bool,
) -> None:
    login(role, userid)
    input = {
        "uuid": carol,
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
        variables=jsonable_encoder(dict(input=input)),
    )
    if success:
        assert_granted(r)
    else:
        assert_denied(r)

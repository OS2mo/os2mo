# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable

import pytest
from mora.mapping import ADMIN
from mora.mapping import OWNER

from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth

# Users
ANDERS_AND = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"
FEDTMULE = "6ee24785-ee9a-4502-81c2-7697009c9053"
LIS_JENSEN = "7626ad64-327d-481f-8b32-36c78eb12f8c"
ERIK_SMIDT_HANSEN = "236e0a78-11a0-4ed9-8545-6286bb8611c7"


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


parametrize_roles = (
    "role, userid, success",
    # Test of write access for the following cases:
    [
        # 1) Normal user (no roles set)
        (None, None, False),
        # 2) User with the owner role, but not owner of the relevant entity
        (OWNER, FEDTMULE, False),
        # 3) User with the owner role and owner of the relative entity
        (OWNER, ANDERS_AND, True),
        # 4) User with the admin role
        (ADMIN, FEDTMULE, True),
    ],
)


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
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "role, userid, success",
    # Test of write access for the following cases:
    [
        # 1) Normal user (no roles set)
        (None, None, False),
        # 2) User with owner role
        (OWNER, ANDERS_AND, False),
        # 3) User with the admin role
        (ADMIN, ANDERS_AND, True),
    ],
)
def test_create_employee(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)
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
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_creating_detail_address(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

    # Payload for creating detail (phone number) on employee
    input = {
        "address_type": "cbadfa0f-ce4f-40b9-86a0-2e85d8961f5d",
        "visibility": "f63ad763-0e53-4972-a6a9-63b42a0f8cb7",
        "employee": LIS_JENSEN,
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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
def test_success_when_creating_it_system_detail_as_owner_of_employee(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
) -> None:
    # Use user "Anders And" (who owns the employee)
    set_auth(OWNER, ANDERS_AND)

    input = {
        "user_key": "AD",
        "person": LIS_JENSEN,
        "itsystem": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
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
        variables=dict(input=input),
    )
    assert r.errors is None


# When creating employee details in the frontend some details actually
# resides under an org unit, e.g. employment, role, association, ...
# A selection of these details are tested here (with respect to creating details)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_employment(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

    input = {
        "person": LIS_JENSEN,
        "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
        "engagement_type": "06f95678-166a-455a-a2ab-121a8d92ea23",
        "job_function": "f42dd694-f1fd-42a6-8a97-38777b73adc4",
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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_association(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

    input = {
        "person": LIS_JENSEN,
        "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
        "association_type": "62ec821f-4179-4758-bfdf-134529d186e9",
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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_fedtmule_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_manager(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

    input = {
        "person": LIS_JENSEN,
        "org_unit": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
        "manager_type": "0d72900a-22a4-4390-a01e-fd65d0e0999d",
        "manager_level": "3c791935-2cfa-46b5-a12e-66f7f54e70fe",
        "responsibility": "93ea44f9-127c-4465-a34c-77d149e3e928",
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
        variables=dict(input=input),
    )
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_erik_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_create_leave(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

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
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

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
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

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
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

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
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)

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
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    mutation: str,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)
    r = graphapi_post(mutation)
    if success:
        assert r.errors is None
    else:
        assert r.errors is not None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "create_lis_owner")
@pytest.mark.parametrize(*parametrize_roles)
def test_terminate_employee(
    set_auth: SetAuth,
    graphapi_post: GraphAPIPost,
    role: str,
    userid: str,
    success: bool,
) -> None:
    set_auth(role, userid)
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

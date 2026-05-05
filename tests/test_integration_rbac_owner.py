# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Protocol
from uuid import UUID

import pytest
from mora.mapping import ADMIN
from mora.mapping import OWNER

from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth


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


CreatePerson = Callable[[], UUID]


@pytest.fixture
async def create_person(graphapi_post: GraphAPIPost) -> CreatePerson:
    def _create_person() -> UUID:
        input = {
            # Nothing here matters
            "given_name": "Foo",
            "surname": "Bar",
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
        if r.errors is not None:
            raise PermissionError(r.errors)
        assert r.data is not None
        return UUID(r.data["employee_create"]["uuid"])

    return _create_person


class CreateOrgUnit(Protocol):
    def __call__(self, parent: UUID | None = None) -> UUID: ...


@pytest.fixture
def create_org_unit(graphapi_post: GraphAPIPost) -> CreateOrgUnit:
    def _create_org_unit(parent: UUID | None = None) -> UUID:
        input = {
            "parent": parent,
            # The rest doesn't matter
            "name": "Foo",
            "org_unit_type": "ca76a441-6226-404f-88a9-31e02e420e52",
            "validity": {
                "from": "2010-01-01",
            },
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
        if r.errors is not None:
            raise PermissionError(r.errors)
        assert r.data is not None
        return UUID(r.data["org_unit_create"]["uuid"])

    return _create_org_unit


class CreateOwner(Protocol):
    def __call__(
        self, owner: UUID, person: UUID | None = None, org_unit: UUID | None = None
    ) -> UUID: ...


@pytest.fixture
def create_owner(graphapi_post: GraphAPIPost) -> CreateOwner:
    def _create_owner(
        owner: UUID, person: UUID | None = None, org_unit: UUID | None = None
    ) -> UUID:
        assert person or org_unit
        input = {
            "owner": str(owner),
            "person": str(person) if person is not None else None,
            "org_unit": str(org_unit) if org_unit is not None else None,
            # The rest doesn't matter
            "validity": {
                "from": "2010-01-01",
            },
        }
        r = graphapi_post(
            """
            mutation OwnerCreate($input: OwnerCreateInput!) {
              owner_create(input: $input) {
                uuid
              }
            }
            """,
            variables=dict(input=input),
        )
        if r.errors is not None:
            raise PermissionError(r.errors)
        assert r.data is not None
        return UUID(r.data["owner_create"]["uuid"])

    return _create_owner


ClearOwners = Callable[[], None]


@pytest.fixture
def clear_owners(graphapi_post: GraphAPIPost) -> ClearOwners:
    def _clear_owners() -> None:
        r = graphapi_post(
            """
            query GetOwners {
              owners {
                objects {
                  uuid
                }
              }
            }
            """
        )
        assert r.errors is None
        assert r.data is not None
        for owner in r.data["owners"]["objects"]:
            r = graphapi_post(
                """
                mutation OwnerTerminate($input: OwnerTerminateInput!) {
                  owner_terminate(input: $input) {
                    uuid
                  }
                }
                """,
                variables=dict(input={"uuid": owner["uuid"], "to": "1900-01-01"}),
            )
            assert r.errors is None

    return _clear_owners


class CreateEngagement(Protocol):
    def __call__(self, person: UUID, org_unit: UUID) -> UUID: ...


@pytest.fixture
async def create_engagement(graphapi_post: GraphAPIPost) -> CreateEngagement:
    def _create_engagement(person: UUID, org_unit: UUID) -> UUID:
        input = {
            "person": str(person),
            "org_unit": str(org_unit),
            # The rest doesn't matter
            "engagement_type": "06f95678-166a-455a-a2ab-121a8d92ea23",
            "job_function": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
            "validity": {
                "from": "2010-01-01",
            },
        }
        r = graphapi_post(
            """
            mutation EngagementCreate($input: EngagementCreateInput!) {
                engagement_create(input: $input) {
                    uuid
                }
            }
            """,
            variables=dict(input=input),
        )
        if r.errors is not None:
            raise PermissionError(r.errors)
        assert r.data is not None
        return UUID(r.data["engagement_create"]["uuid"])

    return _create_engagement


class UpdateEngagement(Protocol):
    def __call__(self, uuid: UUID, person: UUID, org_unit: UUID) -> UUID: ...


@pytest.fixture
async def update_engagement(graphapi_post: GraphAPIPost) -> UpdateEngagement:
    def _update_engagement(uuid: UUID, person: UUID, org_unit: UUID) -> UUID:
        input = {
            "uuid": str(uuid),
            "person": str(person),
            "org_unit": str(org_unit),
            # The rest doesn't matter
            "engagement_type": "06f95678-166a-455a-a2ab-121a8d92ea23",
            "job_function": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
            "validity": {
                "from": "2010-01-01",
            },
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
        if r.errors is not None:
            raise PermissionError(r.errors)
        assert r.data is not None
        return UUID(r.data["engagement_update"]["uuid"])

    return _update_engagement


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_engagement(
    set_auth: SetAuth,
    create_person: CreatePerson,
    create_org_unit: CreateOrgUnit,
    create_owner: CreateOwner,
    create_engagement: CreateEngagement,
) -> None:
    # Setup
    set_auth(ADMIN, None)
    owner = create_person()
    person = create_person()
    org_unit = create_org_unit(parent=None)

    # No owner role or owner object
    set_auth(None, owner)
    with pytest.raises(
        PermissionError, match="User does not have create-access to engagement"
    ):
        create_engagement(person=person, org_unit=org_unit)

    # Owner role, but no owner object
    set_auth(OWNER, owner)
    with pytest.raises(
        PermissionError, match="User does not have create-access to engagement"
    ):
        create_engagement(person=person, org_unit=org_unit)

    # Owner role + owner of org unit
    set_auth(ADMIN, None)
    create_owner(owner=owner, org_unit=org_unit)
    set_auth(OWNER, owner)
    create_engagement(person=person, org_unit=org_unit)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_engagement(
    set_auth: SetAuth,
    create_person: CreatePerson,
    create_org_unit: CreateOrgUnit,
    create_owner: CreateOwner,
    create_engagement: CreateEngagement,
    update_engagement: UpdateEngagement,
    clear_owners: ClearOwners,
) -> None:
    # Setup
    set_auth(ADMIN, None)
    owner = create_person()
    person = create_person()
    old_org_unit = create_org_unit(parent=None)
    new_org_unit = create_org_unit(parent=None)
    engagement = create_engagement(person=person, org_unit=old_org_unit)

    # No owner role or owner object
    set_auth(None, owner)
    with pytest.raises(
        PermissionError, match="User does not have update-access to engagement"
    ):
        update_engagement(uuid=engagement, person=person, org_unit=new_org_unit)

    # Owner role, but no owner object
    set_auth(OWNER, owner)
    with pytest.raises(
        PermissionError, match="User does not have update-access to engagement"
    ):
        update_engagement(uuid=engagement, person=person, org_unit=new_org_unit)

    # Owner role + owner of old org unit, but not new org unit
    set_auth(ADMIN, None)
    clear_owners()
    create_owner(owner=owner, org_unit=old_org_unit)
    set_auth(OWNER, owner)
    with pytest.raises(
        PermissionError, match="User does not have update-access to engagement"
    ):
        update_engagement(uuid=engagement, person=person, org_unit=new_org_unit)

    # Owner role + owner of new org unit, but not old org unit
    set_auth(ADMIN, None)
    clear_owners()
    create_owner(owner=owner, org_unit=new_org_unit)
    set_auth(OWNER, owner)
    with pytest.raises(
        PermissionError, match="User does not have update-access to engagement"
    ):
        update_engagement(uuid=engagement, person=person, org_unit=new_org_unit)

    # Owner role + owner of old *and* new org unit
    set_auth(ADMIN, None)
    clear_owners()
    create_owner(owner=owner, org_unit=old_org_unit)
    create_owner(owner=owner, org_unit=new_org_unit)
    set_auth(OWNER, owner)
    update_engagement(uuid=engagement, person=person, org_unit=new_org_unit)

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from ..conftest import GraphAPIPost
from .utils import fetch_class_uuids
from .utils import fetch_employee_validity


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the manager data model."""
    query = """
        query {
            managers {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        employee_uuid
                        manager_level_uuid
                        manager_type_uuid
                        org_unit_uuid
                        responsibility_uuids
                        type
                        validity {from to}
                    }
                }
            }
        }
    """
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 1),
        # Employee filters
        ({"employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"}, 1),
        ({"employees": "6ee24785-ee9a-4502-81c2-7697009c9053"}, 0),
        (
            {
                "employees": [
                    "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    "6ee24785-ee9a-4502-81c2-7697009c9053",
                ]
            },
            1,
        ),
        # Organisation Unit filter
        ({"org_units": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"}, 1),
        ({"org_units": "2874e1dc-85e6-4269-823a-e1125484dfd3"}, 0),
        (
            {
                "org_units": [
                    "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                ]
            },
            1,
        ),
        # Mixed filters
        (
            {
                "employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_units": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            },
            0,
        ),
        (
            {
                "employees": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                "org_units": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            },
            1,
        ),
        # UUID filter
        ({"uuids": "05609702-977f-4869-9fb4-50ad74c6999a"}, 1),
        ({"uuids": "fa11c0de-baad-baaad-baad-cafebabebad"}, 0),
        # Responsibility filters
        ({"responsibility": {"uuids": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"}}, 1),
        ({"responsibility": {"uuids": "fa11c0de-baad-baaad-baad-cafebabebad"}}, 0),
        ({"responsibility": {"user_keys": "fak"}}, 1),
        ({"responsibility": {"user_keys": "failcode"}}, 0),
    ],
)
async def test_manager_filters(graphapi_post: GraphAPIPost, filter, expected) -> None:
    """Test filters on managers."""
    manager_query = """
        query Managers($filter: ManagerFilter!) {
            managers(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(manager_query, variables=dict(filter=filter))
    assert response.errors is None
    assert len(response.data["managers"]["objects"]) == expected

    # Org-unit filters are implicit in org-unit manager queries, and thus ignored here
    if "org_units" in filter:
        return

    manager_query = """
        query OrgUnitManagers($filter: OrgUnitsboundmanagerfilter!) {
            org_units(filter: {uuids: "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"}) {
                objects {
                    current {
                        managers(filter: $filter) {
                            uuid
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(manager_query, variables=dict(filter=filter))
    assert response.errors is None
    org_unit = one(response.data["org_units"]["objects"])
    assert len(org_unit["current"]["managers"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_create_manager_integration_test(
    graphapi_post: GraphAPIPost, employee_uuids, org_uuids
) -> None:
    """Test that managers can be created in LoRa via GraphQL."""

    # This must be done as to not receive validation errors of the employee upon
    # creating the employee conflicting the dates.
    employee_uuid = employee_uuids[0]
    parent_from, parent_to = fetch_employee_validity(graphapi_post, employee_uuid)

    start_date = parent_from

    manager_level_uuids = fetch_class_uuids(graphapi_post, "manager_level")
    manager_type_uuids = fetch_class_uuids(graphapi_post, "manager_type")
    responsibility_uuids = fetch_class_uuids(graphapi_post, "responsibility")

    test_data = {
        "uuid": str(uuid4()),
        "user_key": "asd123",
        "person": str(employee_uuid),
        "responsibility": [str(u) for u in responsibility_uuids],
        "org_unit": str(org_uuids[0]),
        "manager_type": str(manager_type_uuids[0]),
        "manager_level": str(manager_level_uuids[0]),
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutation = """
        mutation CreateManager($input: ManagerCreateInput!) {
            manager_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutation, {"input": test_data})
    assert response.errors is None
    assert response.data is not None
    uuid = UUID(response.data["manager_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            managers(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        user_key
                        type
                        employee: employee_uuid
                        responsibility: responsibility_uuids
                        org_unit: org_unit_uuid
                        manager_type: manager_type_uuid
                        manager_level: manager_level_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(one(response.data["managers"]["objects"])["objects"])

    assert obj["responsibility"] == test_data["responsibility"]
    assert obj["org_unit"] == test_data["org_unit"]
    assert obj["employee"] == test_data["person"]
    assert obj["manager_type"] == test_data["manager_type"]
    assert obj["manager_level"] == test_data["manager_level"]
    assert obj["user_key"] == test_data["user_key"]
    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": None,
            "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "responsibility": None,
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "manager_level": None,
            "manager_type": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": None,
            "person": None,
            "responsibility": None,
            "org_unit": None,
            "manager_type": None,
            "manager_level": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": None,
            "person": None,
            "responsibility": ["93ea44f9-127c-4465-a34c-77d149e3e928"],
            "org_unit": None,
            "manager_level": None,
            "manager_type": None,
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": "-",
            "person": None,
            "responsibility": None,
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "manager_level": "ca76a441-6226-404f-88a9-31e02e420e52",
            "manager_type": "a22f8575-89b4-480b-a7ba-b3f1372e25a4",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "05609702-977f-4869-9fb4-50ad74c6999a",
            "user_key": "-",
            "person": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
            "responsibility": [
                "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
                "452e1dd0-658b-477a-8dd8-efba105c06d6",
                "93ea44f9-127c-4465-a34c-77d149e3e928",
            ],
            "org_unit": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "manager_level": "d56f174d-c45d-4b55-bdc6-c57bf68238b9",
            "manager_type": "a22f8575-89b4-480b-a7ba-b3f1372e25a4",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
    ],
)
async def test_update_manager_integration_test(
    test_data, graphapi_post: GraphAPIPost
) -> None:
    """Test that managers can be updated in LoRa via GraphQL."""

    uuid = test_data["uuid"]

    query = """
        query MyQuery($uuid: UUID!) {
            managers(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        user_key
                        person: employee_uuid
                        responsibility: responsibility_uuids
                        org_unit: org_unit_uuid
                        manager_type: manager_type_uuid
                        manager_level: manager_level_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(query, {"uuid": str(uuid)})
    assert response.errors is None

    pre_update_manager = one(one(response.data["managers"]["objects"])["objects"])

    mutation = """
        mutation UpdateManager($input: ManagerUpdateInput!) {
            manager_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(test_data)})

    assert mutation_response.errors is None

    # Writing verify query to retrieve objects containing data on the desired uuids.
    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            managers(filter: {uuids: [$uuid]}){
                objects {
                    objects {
                        uuid
                        user_key
                        person: employee_uuid
                        responsibility: responsibility_uuids
                        org_unit: org_unit_uuid
                        manager_type: manager_type_uuid
                        manager_level: manager_level_uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """

    verify_response = graphapi_post(verify_query, {"uuid": str(uuid)})
    assert verify_response.errors is None

    manager_objects_post_update = one(
        one(verify_response.data["managers"]["objects"])["objects"]
    )

    expected_updated_manager = {
        k: v if v is not None or k == "person" else pre_update_manager[k]
        for k, v in test_data.items()
    }

    # Sort lists of relations to ensure deterministic comparison, as LoRa does
    # not guarantee retrieval order (consistent with test_integration_ituser.py).
    if "responsibility" in manager_objects_post_update:
        manager_objects_post_update["responsibility"].sort()
    if "responsibility" in expected_updated_manager:
        expected_updated_manager["responsibility"].sort()

    assert manager_objects_post_update == expected_updated_manager


async def read_manager_validities(
    graphapi_post: GraphAPIPost, uuid: UUID
) -> list[dict[str, Any]]:
    query = """
        query ReadManager($uuid: UUID!) {
          managers(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
            objects {
              objects {
                employee_uuid
                uuid
                validity {
                    from
                    to
                }
              }
            }
          }
        }
    """
    query_response = graphapi_post(query, {"uuid": str(uuid)})
    assert query_response.errors is None
    manager_validities = one(query_response.data["managers"]["objects"])
    return manager_validities["objects"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_manager_vacate_integration_test(
    graphapi_post: GraphAPIPost,
) -> None:
    """Test that managers can be vacated via GraphQL."""

    employee_uuid = UUID("53181ed2-f1de-4c4a-a8fd-ab358c2c454a")
    uuid = UUID("05609702-977f-4869-9fb4-50ad74c6999a")

    manager_validities = await read_manager_validities(graphapi_post, uuid)
    assert manager_validities == [
        {
            "employee_uuid": str(employee_uuid),
            "uuid": str(uuid),
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        }
    ]

    mutation = """
        mutation TerminateManager($input: ManagerUpdateInput!) {
            manager_update(input: $input) {
                uuid
            }
        }
    """
    input = {"uuid": uuid, "validity": {"from": datetime(2020, 1, 1)}, "person": None}
    mutation_response = graphapi_post(mutation, {"input": jsonable_encoder(input)})
    assert mutation_response.errors is None
    assert UUID(mutation_response.data["manager_update"]["uuid"]) == uuid

    # Verify change
    manager_validities = await read_manager_validities(graphapi_post, uuid)
    assert manager_validities == [
        {
            "employee_uuid": str(employee_uuid),
            "uuid": str(uuid),
            "validity": {
                "from": "2017-01-01T00:00:00+01:00",
                "to": "2019-12-31T00:00:00+01:00",
            },
        },
        {
            "employee_uuid": None,
            "uuid": str(uuid),
            "validity": {"from": "2020-01-01T00:00:00+01:00", "to": None},
        },
    ]


@pytest.fixture
def manager(graphapi_post: GraphAPIPost) -> UUID:
    person_uuid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"  # Anders And

    create_manager = graphapi_post(
        """
        mutation CreateManager($input: ManagerCreateInput!) {
          manager_create(input: $input) {
            uuid
          }
        }
        """,
        variables={
            "input": {
                "person": person_uuid,
                "responsibility": ["4311e351-6a3c-4e7e-ae60-8a3b2938fbd6"],
                "org_unit": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "manager_level": "ca76a441-6226-404f-88a9-31e02e420e52",
                "manager_type": "32547559-cfc1-4d97-94c6-70b192eff825",
                "validity": {"from": "2021-01-01"},
            }
        },
    )

    assert create_manager.errors is None
    assert create_manager.data is not None
    return UUID(create_manager.data["manager_create"]["uuid"])


def read_managers(
    graphapi_post: GraphAPIPost, filter: dict[str, Any], inherit: bool = True
) -> list[UUID]:
    response = """
        query ReadManager($filter: ManagerFilter!, $inherit: Boolean!) {
            managers(filter: $filter, inherit: $inherit) {
                objects {
                    current {
                        uuid
                    }
                }
            }
        }
    """
    response = graphapi_post(response, variables={"filter": filter, "inherit": inherit})
    if response.errors:
        raise ValueError(response.errors)
    assert response.data
    return [
        UUID(manager["current"]["uuid"])
        for manager in response.data["managers"]["objects"]
        if manager["current"] is not None
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_inherit_current(
    graphapi_post: GraphAPIPost,
    manager: UUID,
) -> None:
    child_units = (
        "b688513d-11f7-4efc-b679-ab082a2055d0",  # Samfundsvidenskabelige fakultet
    )
    managers = read_managers(graphapi_post, {"org_unit": {"uuids": child_units}})
    assert managers == [manager]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "manager")
def test_exclude(graphapi_post: GraphAPIPost) -> None:
    person_uuid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"  # Anders And
    child_units = (
        "b688513d-11f7-4efc-b679-ab082a2055d0",  # Samfundsvidenskabelige fakultet
    )
    managers = read_managers(
        graphapi_post,
        {"org_unit": {"uuids": child_units}, "exclude": {"uuids": person_uuid}},
    )
    assert managers == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_inherit_current_org_units_filter(
    graphapi_post: GraphAPIPost,
    manager: UUID,
) -> None:
    child_units = (
        "b688513d-11f7-4efc-b679-ab082a2055d0",  # Samfundsvidenskabelige fakultet
    )
    managers = read_managers(graphapi_post, {"org_units": child_units})
    assert managers == [manager]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_inherit_non_existent(graphapi_post: GraphAPIPost) -> None:
    managers = read_managers(graphapi_post, {"org_unit": {"uuids": [str(uuid4())]}})
    assert managers == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_inherit_non_existent_org_units_filter(graphapi_post: GraphAPIPost) -> None:
    managers = read_managers(graphapi_post, {"org_units": [str(uuid4())]})
    assert managers == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "manager")
def test_inherit_works_with_only_one_org_unit(graphapi_post: GraphAPIPost) -> None:
    """Test that we can only use inherit with atmost one org-unit."""
    child_units = (
        "b688513d-11f7-4efc-b679-ab082a2055d0",  # Samfundsvidenskabelige fakultet
        "68c5d78e-ae26-441f-a143-0103eca8b62a",  # Social og sundhed
    )
    with pytest.raises(ValueError) as exc_info:
        read_managers(graphapi_post, {"org_unit": {"uuids": child_units}})
    assert "The inherit flag only works with at most one organisational unit" in str(
        exc_info.value
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "manager")
def test_inherit_requires_org_unit_filter(graphapi_post: GraphAPIPost) -> None:
    """Test that inherit requires an org-unit filter."""
    with pytest.raises(ValueError) as exc_info:
        read_managers(graphapi_post, {"uuids": [str(uuid4())]})
    assert "The inherit flag requires an organizational unit filter" in str(
        exc_info.value
    )


def read_org_units_managers(
    graphapi_post: GraphAPIPost,
    org_unit_filter: dict[str, Any],
    manager_filter: dict[str, Any] | None = None,
    inherit: bool = True,
) -> list[UUID]:
    response = """
        query ReadOrgUnitsManager(
            $org_unit_filter: OrganisationUnitFilter!,
            $manager_filter: OrgUnitsboundmanagerfilter,
            $inherit: Boolean!
        ) {
            org_units(filter: $org_unit_filter) {
                objects {
                    current {
                        managers(filter: $manager_filter, inherit: $inherit) {
                            uuid
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(
        response,
        variables={
            "org_unit_filter": org_unit_filter,
            "manager_filter": manager_filter,
            "inherit": inherit,
        },
    )
    if response.errors:
        raise ValueError(response.errors)
    assert response.data
    return [
        UUID(manager["uuid"])
        for org_unit in response.data["org_units"]["objects"]
        for manager in org_unit["current"]["managers"]
        if org_unit["current"] is not None
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_org_unit_inherit_current(
    graphapi_post: GraphAPIPost,
    manager: UUID,
) -> None:
    child_units = (
        "b688513d-11f7-4efc-b679-ab082a2055d0",  # Samfundsvidenskabelige fakultet
    )
    managers = read_org_units_managers(graphapi_post, {"uuids": child_units})
    assert managers == [manager]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "manager")
def test_org_unit_exclude(graphapi_post: GraphAPIPost) -> None:
    person_uuid = "53181ed2-f1de-4c4a-a8fd-ab358c2c454a"  # Anders And
    child_units = (
        "b688513d-11f7-4efc-b679-ab082a2055d0",  # Samfundsvidenskabelige fakultet
    )
    managers = read_org_units_managers(
        graphapi_post, {"uuids": child_units}, {"exclude": {"uuids": person_uuid}}
    )
    assert managers == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_org_unit_inherit_non_existent(graphapi_post: GraphAPIPost) -> None:
    managers = read_org_units_managers(graphapi_post, {"uuids": [str(uuid4())]})
    assert managers == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db", "manager")
def test_org_unit_inherit_works_with_multiple_org_units(
    graphapi_post: GraphAPIPost, manager: UUID
) -> None:
    """Test that we can only use inherit with atmost multiple org-unit."""
    child_units = (
        "b688513d-11f7-4efc-b679-ab082a2055d0",  # Samfundsvidenskabelige fakultet
        "68c5d78e-ae26-441f-a143-0103eca8b62a",  # Social og sundhed
    )
    managers = read_org_units_managers(graphapi_post, {"uuids": child_units})
    assert managers == [manager, manager]


def read_engagement_managers(
    graphapi_post: GraphAPIPost,
    engagement_filter: dict[str, Any] | None = None,
    manager_filter: dict[str, Any] | None = None,
    inherit: bool = True,
) -> list[UUID]:
    response = """
        query ReadOrgUnitsManager(
            $engagement_filter: EngagementFilter,
            $manager_filter: OrgUnitsboundmanagerfilter,
            $inherit: Boolean!
        ) {
            engagements(filter: $engagement_filter) {
                objects {
                    uuid
                    current {
                        managers(filter: $manager_filter, inherit: $inherit) {
                            uuid
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(
        response,
        variables={
            "engagement_filter": engagement_filter,
            "manager_filter": manager_filter,
            "inherit": inherit,
        },
    )
    if response.errors:
        raise ValueError(response.errors)
    assert response.data
    return [
        UUID(manager["uuid"])
        for engagement in response.data["engagements"]["objects"]
        for manager in engagement["current"]["managers"]
        if engagement["current"] is not None
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_engagement_inherit_current(graphapi_post: GraphAPIPost) -> None:
    engagement = "301a906b-ef51-4d5c-9c77-386fb8410459"
    manager = UUID("05609702-977f-4869-9fb4-50ad74c6999a")
    managers = read_engagement_managers(graphapi_post, {"uuids": engagement})
    assert managers == [manager]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_engagement_inherit_current_but_filtered(graphapi_post: GraphAPIPost) -> None:
    engagement = "301a906b-ef51-4d5c-9c77-386fb8410459"
    managers = read_engagement_managers(
        graphapi_post, {"uuids": engagement}, {"employee": {"uuids": [str(uuid4())]}}
    )
    assert managers == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_engagement_inherit_non_existent(graphapi_post: GraphAPIPost) -> None:
    managers = read_engagement_managers(graphapi_post, {"uuids": [str(uuid4())]})
    assert managers == []

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
from functools import partial
from typing import Any
from unittest import TestCase
from uuid import UUID
from uuid import uuid4

import pytest
from mora import util
from mora.graphapi.shim import execute_graphql
from more_itertools import one

from tests.conftest import AnotherTransaction

from ..conftest import GraphAPIPost


def read_classes_helper(
    graphapi_post: GraphAPIPost, query: str, extract: str
) -> dict[UUID, Any]:
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data
    return {UUID(x["uuid"]): x[extract] for x in response.data["classes"]["objects"]}


read_classes = partial(
    read_classes_helper,
    query="""
        query ReadClasses {
            classes {
                objects {
                    uuid
                    current {
                        uuid
                        user_key
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """,
    extract="current",
)

read_history = partial(
    read_classes_helper,
    query="""
        query ReadClasses {
            classes(filter: {from_date: null, to_date: null}) {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """,
    extract="objects",
)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all attributes of the classes data model."""
    query = """
        query {
            classes {
                objects {
                    current {
                        uuid
                        user_key
                        facet_uuid
                        example
                        owner
                        org_uuid
                        name
                        parent_uuid
                        published
                        scope
                        type
                        it_system_uuid
                        validity {
                            from
                            to
                        }
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
async def test_integration_create_class(
    graphapi_post: GraphAPIPost,
    another_transaction: AnotherTransaction,
) -> None:
    """Integrationtest for create class mutator."""

    mutate_query = """
        mutation CreateClass($input: ClassCreateInput!) {
          class_create(input: $input) {
            uuid
          }
        }
    """

    uuid = str(uuid4())
    facet_uuid = str(uuid4())
    mut_response = graphapi_post(
        query=mutate_query,
        variables={
            "input": {
                "uuid": uuid,
                "user_key": "test_class",
                "facet_uuid": facet_uuid,
                "name": "Test Class",
                "validity": {
                    "from": "2021-01-01T00:00:00+01:00",
                    "to": None,
                },
            }
        },
    )

    assert mut_response.errors is None
    assert mut_response.data

    response_uuid = mut_response.data["class_create"]["uuid"]

    """Query data to check that it actually gets written to database"""
    query_query = """
        query ($uuid: [UUID!]!) {
          classes(filter: {uuids: $uuid}) {
            objects {
              current {
                uuid
                type
                user_key
                name
                facet_uuid
                parent_uuid
                it_system_uuid
                validity {
                  from
                  to
                }
              }
            }
          }
        }
    """
    async with another_transaction():
        query_response = await execute_graphql(
            query=query_query,
            variable_values={"uuid": str(response_uuid)},
        )

    assert query_response.errors is None
    assert query_response.data is not None

    created_class = one(query_response.data["classes"]["objects"])["current"]
    assert created_class == {
        "uuid": uuid,
        "type": "class",
        "user_key": "test_class",
        "name": "Test Class",
        "facet_uuid": facet_uuid,
        "parent_uuid": None,
        "it_system_uuid": None,
        "validity": {
            "from": "2021-01-01T00:00:00+01:00",
            "to": None,
        },
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 39),
        # Facet filters
        # -------------
        ({"facet_user_keys": "employee_address_type"}, 3),
        ({"facets": "baddc4eb-406e-4c6b-8229-17e4a21d3550"}, 3),
        ({"facet_user_keys": "org_unit_address_type"}, 6),
        ({"facets": "3c44e5d2-7fef-4448-9bf6-449bf414ec49"}, 6),
        ({"facet_user_keys": ["employee_address_type", "org_unit_address_type"]}, 9),
        (
            {
                "facets": [
                    "baddc4eb-406e-4c6b-8229-17e4a21d3550",
                    "3c44e5d2-7fef-4448-9bf6-449bf414ec49",
                ]
            },
            9,
        ),
        # Scope filters
        # -------------
        ({"scope": ""}, 0),
        ({"scope": "360NoScope"}, 0),
        # Address type scopes
        ({"scope": "DAR"}, 2),
        ({"scope": "EMAIL"}, 2),
        ({"scope": "EAN"}, 1),
        ({"scope": "PHONE"}, 2),
        ({"scope": "WWW"}, 0),
        # Text input scopes
        ({"scope": "TEXT"}, 6),
        ({"scope": "INTEGER"}, 0),
        # Engagement type scopes
        ({"scope": "10"}, 1),
        ({"scope": "3000"}, 1),
    ],
)
async def test_class_filter(graphapi_post: GraphAPIPost, filter, expected) -> None:
    """Test class filters on classes."""
    class_query = """
        query Classes($filter: ClassFilter!) {
            classes(filter: $filter) {
                objects {
                    current {
                        uuid
                    }
                }
            }
        }
    """
    response = graphapi_post(class_query, variables=dict(filter=filter))
    assert response.errors is None
    assert len(response.data["classes"]["objects"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_integration_delete_class() -> None:
    read_query = """
        query ($uuid: [UUID!]!) {
          classes(filter: {uuids: $uuid}) {
            objects {
              current {
                uuid
                name
              }
            }
          }
        }
    """
    class_uuid = "4e337d8e-1fd2-4449-8110-e0c8a22958ed"

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": class_uuid},
    )
    assert response.errors is None
    assert response.data == {
        "classes": {
            "objects": [{"current": {"name": "Postadresse", "uuid": class_uuid}}]
        }
    }

    delete_query = """
        mutation ($uuid: UUID!) {
          class_delete(uuid: $uuid) {
            uuid
          }
        }
    """
    response = await execute_graphql(
        query=delete_query,
        variable_values={"uuid": class_uuid},
    )
    assert response.errors is None
    assert response.data == {"class_delete": {"uuid": class_uuid}}

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": class_uuid},
    )
    assert response.errors is None
    assert response.data == {"classes": {"objects": []}}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_update_class() -> None:
    """Unit test for create class mutator."""
    read_query = """
        query ($uuid: [UUID!]!) {
          classes(filter: {uuids: $uuid}) {
            objects {
              current {
                uuid
                name
                user_key
                facet_uuid
                validity {
                    from
                    to
                }
              }
            }
          }
        }
    """
    class_uuid = "4e337d8e-1fd2-4449-8110-e0c8a22958ed"

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": class_uuid},
    )
    assert response.errors is None
    assert one(response.data.keys()) == "classes"
    klass = one(response.data["classes"]["objects"])["current"]
    assert klass == {
        "uuid": class_uuid,
        "name": "Postadresse",
        "facet_uuid": "baddc4eb-406e-4c6b-8229-17e4a21d3550",
        "user_key": "BrugerPostadresse",
        "validity": {
            "from": "2016-01-01T00:00:00+01:00",
            "to": None,
        },
    }

    update_query = """
        mutation UpdateClass($input: ClassUpdateInput!) {
            class_update(input: $input) {
                uuid
            }
        }
    """

    dt_now = datetime.datetime.combine(
        datetime.datetime.now().date(), datetime.time.min
    ).replace(tzinfo=util.DEFAULT_TIMEZONE)

    response = await execute_graphql(
        query=update_query,
        variable_values={
            "input": {
                "uuid": class_uuid,
                "name": "Postal Address",
                "user_key": klass["user_key"],
                "facet_uuid": klass["facet_uuid"],
                "validity": {"from": dt_now.date().isoformat()},
            },
        },
    )
    assert response.errors is None
    assert response.data == {"class_update": {"uuid": class_uuid}}

    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": class_uuid},
    )
    assert response.errors is None
    assert one(response.data.keys()) == "classes"
    klass = one(response.data["classes"]["objects"])["current"]
    assert klass == {
        "uuid": class_uuid,
        "name": "Postal Address",
        "facet_uuid": "baddc4eb-406e-4c6b-8229-17e4a21d3550",
        "user_key": "BrugerPostadresse",
        "validity": {
            "from": dt_now.isoformat(),
            "to": None,
        },
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_update_class_parent(
    graphapi_post: GraphAPIPost,
    root_org: UUID,
) -> None:
    # Create test facet
    facet = graphapi_post(
        """
        mutation CreateFacet {
          facet_create(input: {user_key: "test", validity: {from: "2000-01-01"}}) {
            uuid
          }
        }
        """
    )
    assert facet.errors is None
    assert facet.data is not None
    test_facet_uuid = facet.data["facet_create"]["uuid"]

    read_query = """
    query ReadClasses {
      classes(filter: {user_keys: "bar"}) {
        objects {
          current {
            parent {
              uuid
            }
          }
        }
      }
    }
    """
    create_mutation = """
    mutation CreateClass($input: ClassCreateInput!) {
      class_create(input: $input) {
        uuid
      }
    }
    """
    update_mutation = """
    mutation UpdateClass($input: ClassUpdateInput!) {
      class_update(input: $input) {
        uuid
      }
    }
    """

    # Create foo class
    foo = graphapi_post(
        create_mutation,
        variables={
            "input": {
                "name": "foo",
                "user_key": "foo",
                "parent_uuid": None,
                "facet_uuid": test_facet_uuid,
                "validity": {"from": "2020-01-01"},
            },
        },
    )
    assert foo.errors is None
    assert foo.data is not None
    foo_uuid = foo.data["class_create"]["uuid"]

    # Create bar class
    bar = graphapi_post(
        create_mutation,
        variables={
            "input": {
                "name": "bar",
                "user_key": "bar",
                "parent_uuid": foo_uuid,
                "facet_uuid": test_facet_uuid,
                "validity": {"from": "2020-01-01"},
            },
        },
    )
    assert bar.errors is None
    assert bar.data is not None
    bar_uuid = bar.data["class_create"]["uuid"]

    # Verify
    r = graphapi_post(read_query)
    assert r.errors is None
    assert r.data is not None
    assert r.data["classes"]["objects"] == [{"current": {"parent": {"uuid": foo_uuid}}}]

    # Clear bar's parent
    r = graphapi_post(
        update_mutation,
        variables={
            "input": {
                "uuid": bar_uuid,
                "parent_uuid": None,
                "validity": {"from": "2020-01-01"},
                # The rest doesn't matter, but is required because MO doesn't
                # support patch-writes.
                "name": "bar",
                "user_key": "bar",
                "facet_uuid": test_facet_uuid,
            },
        },
    )
    assert r.errors is None

    # Verify
    r = graphapi_post(read_query)
    assert r.errors is None
    assert r.data is not None
    assert r.data["classes"]["objects"] == [{"current": {"parent": None}}]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_terminate_class(graphapi_post) -> None:
    """Test that we can terminate class."""

    # test class: "Niveau1"
    class_to_terminate = UUID("3c791935-2cfa-46b5-a12e-66f7f54e70fe")

    # Verify existing state
    classes_map = read_classes(graphapi_post)
    assert len(classes_map.keys()) == 39
    assert class_to_terminate in classes_map.keys()

    # Terminate the class
    mutation = """
        mutation TerminateClass($input: ClassTerminateInput!) {
            class_terminate(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(
        mutation,
        {"input": {"uuid": str(class_to_terminate), "to": "1990-01-01"}},
    )
    assert response.errors is None
    assert response.data
    terminated_uuid = UUID(response.data["class_terminate"]["uuid"])
    assert terminated_uuid == class_to_terminate

    # Verify class history
    new_class_map = read_history(graphapi_post)
    assert new_class_map.keys() == set(classes_map.keys())

    # Verify class history
    class_history = new_class_map[terminated_uuid]
    assert class_history == [
        {
            "uuid": str(class_to_terminate),
            "user_key": "Niveau1",
            "validity": {
                "from": "1900-01-01T00:00:00+01:00",
                "to": "1990-01-01T00:00:00+01:00",
            },
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_integration_it_system() -> None:
    role_type_facet_uuid = "68ba77bc-4d57-43e2-9c24-0c9eda5fddc7"
    sap_it_system_uuid = "14466fb0-f9de-439c-a6c2-b3262c367da7"
    ad_it_system_uuid = "59c135c9-2b15-41cc-97c8-b5dff7180beb"

    # Create
    create_response = await execute_graphql(
        query="""
            mutation Create($facet_uuid: UUID!, $it_system_uuid: UUID!) {
              class_create(
                input: {
                    facet_uuid: $facet_uuid,
                    user_key: "test",
                    name: "test",
                    it_system_uuid: $it_system_uuid,
                    validity: {from: "2010-02-03"}
                }
              ) {
                uuid
              }
            }
        """,
        variable_values={
            "facet_uuid": role_type_facet_uuid,
            "it_system_uuid": sap_it_system_uuid,
        },
    )
    assert create_response.errors is None
    class_uuid = create_response.data["class_create"]["uuid"]

    # Verify
    read_query = """
        query Read($uuid: UUID!) {
          classes(filter: {uuids: [$uuid]}) {
            objects {
              current {
                it_system {
                  uuid
                }
              }
            }
          }
        }
    """
    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": class_uuid},
    )
    assert response.errors is None
    assert response.data == {
        "classes": {
            "objects": [{"current": {"it_system": {"uuid": sap_it_system_uuid}}}]
        }
    }

    # Update
    update_response = await execute_graphql(
        query="""
            mutation Update(
                $class_uuid: UUID!,
                $facet_uuid: UUID!,
                $it_system_uuid: UUID!,
            ) {
              class_update(
                input: {
                    uuid: $class_uuid,
                    facet_uuid: $facet_uuid,
                    user_key: "test",
                    name: "test",
                    it_system_uuid: $it_system_uuid,
                    validity: {from: "2020-03-04"}
                }
              ) {
                uuid
              }
            }
        """,
        variable_values={
            "class_uuid": class_uuid,
            "facet_uuid": role_type_facet_uuid,
            "it_system_uuid": ad_it_system_uuid,
        },
    )
    assert update_response.errors is None

    # Verify
    response = await execute_graphql(
        query=read_query,
        variable_values={"uuid": class_uuid},
    )
    assert response.errors is None
    assert response.data == {
        "classes": {
            "objects": [{"current": {"it_system": {"uuid": ad_it_system_uuid}}}]
        }
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_integration_it_system_filter() -> None:
    role_type_facet_uuid = "68ba77bc-4d57-43e2-9c24-0c9eda5fddc7"
    sap_it_system_uuid = "14466fb0-f9de-439c-a6c2-b3262c367da7"
    ad_it_system_uuid = "59c135c9-2b15-41cc-97c8-b5dff7180beb"

    # Create
    create_mutation = """
        mutation Create(
            $facet_uuid: UUID!,
            $it_system_uuid: UUID!,
            $user_key: String!,
        ) {
          class_create(
            input: {
                facet_uuid: $facet_uuid,
                user_key: $user_key,
                name: "test",
                it_system_uuid: $it_system_uuid,
                validity: {from: "2010-02-03"}
            }
          ) {
            uuid
          }
        }
    """
    await execute_graphql(
        query=create_mutation,
        variable_values={
            "facet_uuid": role_type_facet_uuid,
            "it_system_uuid": sap_it_system_uuid,
            "user_key": "sap",
        },
    )
    await execute_graphql(
        query=create_mutation,
        variable_values={
            "facet_uuid": role_type_facet_uuid,
            "it_system_uuid": ad_it_system_uuid,
            "user_key": "ad",
        },
    )

    # Filter SAP
    read_query = """
        query Read($it_system_uuid: UUID!) {
          classes(filter: {it_system: {uuids: [$it_system_uuid]}}) {
            objects {
              current {
                user_key
              }
            }
          }
        }
    """
    response = await execute_graphql(
        query=read_query,
        variable_values={"it_system_uuid": sap_it_system_uuid},
    )
    assert response.errors is None
    assert response.data == {"classes": {"objects": [{"current": {"user_key": "sap"}}]}}

    # Filter AD
    response = await execute_graphql(
        query=read_query,
        variable_values={"it_system_uuid": ad_it_system_uuid},
    )
    assert response.errors is None
    assert response.data == {"classes": {"objects": [{"current": {"user_key": "ad"}}]}}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_integration_names_filter(graphapi_post: GraphAPIPost) -> None:
    # Create
    primary_type_facet_uuid = "1f6f34d8-d065-4bb7-9af0-738d25dc0fbf"
    create_mutation = """
        mutation Create($facet_uuid: UUID!, $name: String!) {
          class_create(
            input: {
              facet_uuid: $facet_uuid,
              user_key: "-",
              name: $name,
              scope: "TEXT",
              validity: {from: "2001-02-03"}
            }
          ) {
            uuid
          }
        }
    """
    graphapi_post(
        create_mutation,
        {
            "facet_uuid": primary_type_facet_uuid,
            "name": "foo",
        },
    )
    graphapi_post(
        create_mutation,
        {
            "facet_uuid": primary_type_facet_uuid,
            "name": "bar",
        },
    )
    graphapi_post(
        create_mutation,
        {
            "facet_uuid": primary_type_facet_uuid,
            "name": "baz",
        },
    )

    # Filter multiple names
    read_query = """
        query ClassNamesQuery {
          classes(filter: {name: ["foo", "bar"]}) {
            objects {
              current {
                name
              }
            }
          }
        }
    """
    response = graphapi_post(read_query)
    assert response.errors is None
    TestCase().assertCountEqual(
        response.data["classes"]["objects"],
        [
            {
                "current": {
                    "name": "foo",
                }
            },
            {
                "current": {
                    "name": "bar",
                }
            },
        ],
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_integration_scopes_filter(graphapi_post: GraphAPIPost) -> None:
    # Create
    primary_type_facet_uuid = "1f6f34d8-d065-4bb7-9af0-738d25dc0fbf"
    create_mutation = """
        mutation Create($facet_uuid: UUID!, $scope: String!) {
          class_create(
            input: {
              facet_uuid: $facet_uuid,
              user_key: $scope,
              name: $scope,
              scope: $scope,
              validity: {from: "2001-02-03"}
            }
          ) {
            uuid
          }
        }
    """
    graphapi_post(
        create_mutation,
        {
            "facet_uuid": primary_type_facet_uuid,
            "scope": "OKP-7",
        },
    )
    graphapi_post(
        create_mutation,
        {
            "facet_uuid": primary_type_facet_uuid,
            "scope": "Red Dot",
        },
    )
    graphapi_post(
        create_mutation,
        {
            "facet_uuid": primary_type_facet_uuid,
            "scope": "Holographic",
        },
    )

    # Filter multiple scopes
    read_query = """
        query ClassScopesQuery {
          classes(filter: {scope: ["OKP-7", "Red Dot"]}) {
            objects {
              current {
                user_key
                name
                scope
              }
            }
          }
        }
    """
    response = graphapi_post(read_query)
    assert response.errors is None
    TestCase().assertCountEqual(
        response.data["classes"]["objects"],
        [
            {
                "current": {
                    "user_key": "OKP-7",
                    "name": "OKP-7",
                    "scope": "OKP-7",
                }
            },
            {
                "current": {
                    "user_key": "Red Dot",
                    "name": "Red Dot",
                    "scope": "Red Dot",
                }
            },
        ],
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_integration_class_owner_filter(graphapi_post: GraphAPIPost) -> None:
    org_unit_type_facet_uuid = "fc917e7c-fc3b-47c2-8aa5-a0383342a280"

    # Overordnet enhed
    org_unit_overordnet_enhed = "2874e1dc-85e6-4269-823a-e1125484dfd3"
    # Humanistisk fakultet - child of "Overordnet enhed"
    org_unit_hum = "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"

    # Lønorganisation
    org_unit_loen = "b1f69701-86d8-496e-a3f1-ccef18ac1958"

    # Create
    create_mutation = """
        mutation Create(
            $facet_uuid: UUID!,
            $owner_uuid: UUID!,
            $class_name: String!
        ) {
          class_create(
            input: {
                facet_uuid: $facet_uuid,
                user_key: $class_name,
                name: $class_name,
                owner: $owner_uuid,
                validity: {from: "2010-02-03"}
            }
          ) {
            uuid
          }
        }
    """
    graphapi_post(
        create_mutation,
        {
            "facet_uuid": org_unit_type_facet_uuid,
            "owner_uuid": org_unit_overordnet_enhed,
            "class_name": "class1",
        },
    )
    graphapi_post(
        create_mutation,
        {
            "facet_uuid": org_unit_type_facet_uuid,
            "owner_uuid": org_unit_loen,
            "class_name": "class2",
        },
    )

    read_query = """
        query OwnerClassQuery($facet_uuid: [UUID!], $org_unit_hum: [UUID!]) {
            classes(filter: { facet: { uuids: $facet_uuid } }) {
                objects {
                    current {
                        name
                        uuid
                    }
                }
            }
            exclude_none: classes(
                filter: {
                    facet: { user_keys: "org_unit_type" }
                    owner: { descendant: { uuids: $org_unit_hum }, include_none: false }
                }
            ) {
                objects {
                    current {
                        name
                        uuid
                    }
                }
            }
            include_none: classes(
                filter: {
                    facet: { user_keys: "org_unit_type" }
                    owner: { descendant: { uuids: $org_unit_hum }, include_none: true }
                }
            ) {
                objects {
                    current {
                        name
                        uuid
                    }
                }
            }
        }

    """
    response = graphapi_post(
        read_query,
        variables={
            "facet_uuid": org_unit_type_facet_uuid,
            "org_unit_hum": org_unit_hum,
        },
    )
    all_classes = len(response.data["classes"]["objects"])
    exclude_none = len(response.data["exclude_none"]["objects"])
    include_none = len(response.data["include_none"]["objects"])

    # Expect to only return the class that has the owner "Overordnet enhed"
    assert exclude_none == 1
    # Expect to return all classes except the class that has the owner "Lønorganisation",
    # since it's in a seperate tree to "Overordnet enhed"
    assert include_none == all_classes - 1


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_class_description(
    graphapi_post: GraphAPIPost,
):
    def read_class_description(uuid):
        response = graphapi_post(
            """
          query CreateClass($uuid: UUID!) {
            classes(filter: {uuids: [$uuid]}) {
              objects {
                current {
                  description
                }
              }
            }
          }
        """,
            variables={"uuid": uuid},
        )
        return response.data["classes"]["objects"][0]["current"]["description"]

    response = graphapi_post(
        """
      mutation CreateClass {
        class_create(
          input: {
            facet_uuid: "fc917e7c-fc3b-47c2-8aa5-a0383342a280"
            name: "Et klassenavn"
            user_key: "En brugervendtnøgle"
            description: "en beskrivelse"
            validity: { from: "2024-03-01" }
          }
        ) {
          uuid
        }
      }
    """
    )
    uuid = response.data["class_create"]["uuid"]
    assert "en beskrivelse" == read_class_description(uuid)

    response = graphapi_post(
        """
      mutation UpdateClass($uuid: UUID!) {
        class_update(
          input: {
            uuid: $uuid
            facet_uuid: "fc917e7c-fc3b-47c2-8aa5-a0383342a280"
            name: "Et klassenavn"
            user_key: "En brugervendtnøgle"
            description: "en ny beskrivelse"
            validity: { from: "2024-06-01" }
          }
        ) {
          uuid
        }
      }
    """,
        variables={"uuid": uuid},
    )
    assert "en ny beskrivelse" == read_class_description(uuid)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_empty_name(graphapi_post: GraphAPIPost):
    """Test that classes with empty names can be read."""
    graphql_mutation = """
      mutation CreateClass {
        class_create(
          input: {
            facet_uuid: "fc917e7c-fc3b-47c2-8aa5-a0383342a280"
            name: ""
            user_key: "En brugervendtnøgle"
            description: "en beskrivelse"
            validity: { from: "2024-03-01" }
          }
        ) {
          uuid
          current {
            name
          }
        }
      }
    """
    response = graphapi_post(query=graphql_mutation)
    assert response.errors is None
    assert response.data is not None
    assert response.data["class_create"]["current"]["name"] == ""

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import partial
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one
from strawberry import UNSET
from strawberry.types.unset import UnsetType

from ..conftest import GraphAPIPost
from .utils import fetch_class_uuids
from .utils import fetch_org_unit_validity
from .utils import gen_read_parent
from .utils import gen_set_parent
from .utils import sjsonable_encoder


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
def test_query_all(graphapi_post: GraphAPIPost):
    """Test that we can query all our organisation units."""
    query = """
        query {
            org_units {
                objects {
                    uuid
                    objects {
                        uuid
                        user_key
                        name
                        type
                        validity {from to}
                        parent_uuid
                        unit_type_uuid
                        org_unit_hierarchy
                        org_unit_level_uuid
                        time_planning_uuid
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
def test_create_org_unit_integration_test(
    graphapi_post: GraphAPIPost, org_uuids
) -> None:
    """Test that organisation units can be created in LoRa via GraphQL."""
    parent_uuid = org_uuids[0]
    parent_from, parent_to = fetch_org_unit_validity(graphapi_post, parent_uuid)

    start_date = parent_from

    org_unit_type_uuids = fetch_class_uuids(graphapi_post, "org_unit_type")
    time_planning_uuids = fetch_class_uuids(graphapi_post, "time_planning")
    org_unit_level_uuids = fetch_class_uuids(graphapi_post, "org_unit_level")

    test_data = {
        "uuid": str(uuid4()),
        "name": "Integ Unit",
        "user_key": "integ_unit_key",
        "parent": str(parent_uuid),
        "org_unit_type": str(org_unit_type_uuids[0]),
        "time_planning": str(time_planning_uuids[0]),
        "org_unit_level": str(org_unit_level_uuids[0]),
        "org_unit_hierarchy": None,
        "validity": {
            "from": start_date.isoformat(),
            "to": None,
        },
    }

    mutate_query = """
        mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
            org_unit_create(input: $input) {
                uuid
            }
        }
    """
    response = graphapi_post(mutate_query, {"input": test_data})
    assert response.errors is None
    assert response.data is not None
    uuid = UUID(response.data["org_unit_create"]["uuid"])

    verify_query = """
        query VerifyQuery($uuid: UUID!) {
            org_units(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    objects {
                        uuid
                        user_key
                        name
                        parent_uuid
                        unit_type_uuid
                        time_planning_uuid
                        org_unit_level_uuid
                        org_unit_hierarchy_uuid: org_unit_hierarchy
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
    obj = one(one(response.data["org_units"]["objects"])["objects"])
    assert obj["name"] == test_data["name"]
    assert obj["user_key"] == test_data["user_key"]
    assert obj["parent_uuid"] == test_data["parent"]
    assert obj["unit_type_uuid"] == test_data["org_unit_type"]
    assert obj["time_planning_uuid"] == test_data["time_planning"]
    assert obj["org_unit_level_uuid"] == test_data["org_unit_level"]
    assert obj["org_unit_hierarchy_uuid"] is None
    assert test_data["org_unit_hierarchy"] is None
    assert obj["validity"]["from"] == test_data["validity"]["from"]
    assert obj["validity"]["to"] is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 10),
        # Deactivated filter
        ({"names": None}, 10),
        # Filter empty list
        ({"names": []}, 0),
        # Filter unknown name
        ({"names": ["__this__should__never__match__"]}, 0),
        # Filter one known name
        ({"names": ["Filosofisk Institut"]}, 1),
        # Filter one known name, with multiple matches
        ({"names": ["Social og sundhed"]}, 2),
        # Filter multiple known names
        (
            {
                "names": [
                    "Filosofisk Institut",
                    "Humanistisk fakultet",
                ]
            },
            2,
        ),
        # Filter multiple known names, with multiple matches
        (
            {
                "names": [
                    "Filosofisk Institut",
                    "Humanistisk fakultet",
                    "Social og sundhed",
                ]
            },
            4,
        ),
    ],
)
async def test_org_unit_name_filter(
    graphapi_post: GraphAPIPost, filter: dict[str, list[str] | None], expected: int
) -> None:
    """Test name filter on organisation units."""
    org_unit_query = """
        query OrgUnit($filter: OrganisationUnitFilter!) {
            org_units(filter: $filter) {
                objects {
                    current {
                        name
                    }
                    uuid
                }
            }
        }
    """
    response = graphapi_post(org_unit_query, variables=dict(filter=filter))
    assert response.errors is None
    assert response.data is not None
    assert len(response.data["org_units"]["objects"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 10),
        # Filter roots
        ({"parents": None}, 3),
        # Filter under node
        ({"parents": "2874e1dc-85e6-4269-823a-e1125484dfd3"}, 4),
        ({"parents": "b1f69701-86d8-496e-a3f1-ccef18ac1958"}, 1),
        (
            {
                "parents": [
                    "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "b1f69701-86d8-496e-a3f1-ccef18ac1958",
                ]
            },
            5,
        ),
    ],
)
async def test_org_unit_parent_filter(
    graphapi_post: GraphAPIPost, filter, expected
) -> None:
    """Test parent filter on organisation units."""
    org_unit_query = """
        query OrgUnit($filter: OrganisationUnitFilter!) {
            org_units(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(org_unit_query, variables=dict(filter=filter))
    assert response.errors is None
    assert len(response.data["org_units"]["objects"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # Filter none
        ({}, 10),
        ({"hierarchies": None}, 10),
        # Filter 'linjeorg'
        ({"hierarchies": "f805eb80-fdfe-8f24-9367-68ea955b9b9b"}, 2),
        # Filter 'hidden'
        ({"hierarchies": "8c30ab5a-8c3a-566c-bf12-790bdd7a9fef"}, 1),
        # Filter 'selvejet'
        ({"hierarchies": "69de6410-bfe7-bea5-e6cc-376b3302189c"}, 1),
        # Filter 'linjeorg' + 'hidden'
        (
            {
                "hierarchies": [
                    "f805eb80-fdfe-8f24-9367-68ea955b9b9b",
                    "8c30ab5a-8c3a-566c-bf12-790bdd7a9fef",
                ]
            },
            3,
        ),
    ],
)
async def test_org_unit_hierarchy_filter(
    graphapi_post: GraphAPIPost, filter, expected
) -> None:
    """Test hierarchies filter on organisation units."""
    org_unit_query = """
        query OrgUnit($filter: OrganisationUnitFilter!) {
            org_units(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(org_unit_query, variables=dict(filter=filter))
    assert response.errors is None
    assert len(response.data["org_units"]["objects"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_org_unit_root_field(
    graphapi_post: GraphAPIPost,
) -> None:
    """Test hierarchies filter on organisation units."""
    # org_unit in 3rd level. Root is parent's-parent
    filosofisk_institut = "85715fc7-925d-401b-822d-467eb4b163b6"
    root = "2874e1dc-85e6-4269-823a-e1125484dfd3"
    org_unit_query = """
        query OrgUnit($uuids: [UUID!]) {
            org_units(filter: {uuids: $uuids}) {
                objects {
                    current {
                        root {
                            uuid
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(org_unit_query, variables=dict(uuids=filosofisk_institut))
    assert response.errors is None
    assert (
        one(one(response.data["org_units"]["objects"])["current"]["root"])["uuid"]
        == root
    )


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        ({}, 10),
        ({"engagement": {"uuids": []}}, 0),
        # Random engagements by UUIDs only attached to one org-unit
        ({"engagement": {"uuids": ["301a906b-ef51-4d5c-9c77-386fb8410459"]}}, 1),
        ({"engagement": {"uuids": ["d000591f-8705-4324-897a-075e3623f37b"]}}, 1),
        # Random engagement by user-key only attached to one org-unit
        ({"engagement": {"user_keys": ["bvn"]}}, 1),
        # Random engagement by person uuid only attached to one org-unit
        (
            {
                "engagement": {
                    "employee": {"uuids": ["53181ed2-f1de-4c4a-a8fd-ab358c2c454a"]}
                }
            },
            1,
        ),
        ({"engagement": {"employees": ["53181ed2-f1de-4c4a-a8fd-ab358c2c454a"]}}, 1),
        (
            {
                "engagement": {
                    "employee": {"uuids": ["236e0a78-11a0-4ed9-8545-6286bb8611c7"]}
                }
            },
            1,
        ),
        ({"engagement": {"employees": ["236e0a78-11a0-4ed9-8545-6286bb8611c7"]}}, 1),
        # Random engagement by org uuid only attached to one org-unit
        (
            {
                "engagement": {
                    "org_unit": {"uuids": ["9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"]}
                }
            },
            1,
        ),
        ({"engagement": {"org_units": ["9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"]}}, 1),
    ],
)
async def test_org_unit_engagement_filter(
    graphapi_post: GraphAPIPost, filter, expected
) -> None:
    """Test engagement filter on organisation units."""
    org_unit_query = """
        query OrgUnit($filter: OrganisationUnitFilter!) {
            org_units(filter: $filter) {
                objects {
                    uuid
                }
            }
        }
    """
    response = graphapi_post(org_unit_query, variables=dict(filter=filter))
    assert response.errors is None
    assert response.data is not None
    assert len(response.data["org_units"]["objects"]) == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_org_unit_subtree_filter(graphapi_post: GraphAPIPost) -> None:
    """Test subtree filter on organisation units."""
    # Ensure that the subtree filter respects the date filtering by changing the tree
    # from 'root > skole-børn > it_sup' to 'root > skole-børn | it_sup'.
    root = "2874e1dc-85e6-4269-823a-e1125484dfd3"
    skole_born = "dad7d0ad-c7a9-4a94-969d-464337e31fec"
    it_sup = "fa2e23c9-860a-4c90-bcc6-2c0721869a25"
    response = graphapi_post(
        """
        mutation MoveOrgUnit($uuid: UUID!, $parent: UUID!) {
          org_unit_update(
            input: {
                uuid: $uuid,
                parent: $parent,
                validity: {from: "2024-04-04"},
            }
          ) {
            uuid
          }
        }
        """,
        {
            "uuid": it_sup,
            "parent": root,
        },
    )
    assert response.errors is None

    subtree_query = """
        query SubtreeQuery($from_date: DateTime, $to_date: DateTime) {
          org_units(
            filter: {
              from_date: $from_date,
              to_date: $to_date,
              subtree: {
                user_keys: "it_sup",
                from_date: $from_date,
                to_date: $to_date,
              }
            }
          ) {
            objects {
              validities {
                user_key
                uuid
                parent { uuid }
              }
            }
          }
        }
    """
    # Querying before the change should give us the original tree
    response = graphapi_post(
        subtree_query,
        {
            "from_date": "2023-03-03",
            "to_date": "2023-03-04",
        },
    )
    assert response.errors is None
    assert response.data is not None
    assert response.data["org_units"]["objects"] == [
        {
            "validities": [
                {
                    "user_key": "root",
                    "uuid": root,
                    "parent": None,
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "skole-børn",
                    "uuid": skole_born,
                    "parent": {"uuid": root},
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "it_sup",
                    "uuid": it_sup,
                    "parent": {"uuid": skole_born},
                }
            ]
        },
    ]

    # Querying after the change should give us the new tree
    response = graphapi_post(
        subtree_query,
        {
            "from_date": "2025-05-05",
            "to_date": "2025-05-06",
        },
    )
    assert response.errors is None
    assert response.data is not None
    assert response.data["org_units"]["objects"] == [
        {
            "validities": [
                {
                    "user_key": "root",
                    "uuid": root,
                    "parent": None,
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "it_sup",
                    "uuid": it_sup,
                    "parent": {"uuid": root},
                }
            ]
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_org_unit_descendant_filter(graphapi_post: GraphAPIPost) -> None:
    """Test descendant filter on organisation units."""
    # Ensure that the descendant filter respects the date filtering by changing the tree
    # from 'root > skole-børn > it_sup' to 'root > skole-børn | it_sup'.
    root = "2874e1dc-85e6-4269-823a-e1125484dfd3"
    skole_born = "dad7d0ad-c7a9-4a94-969d-464337e31fec"
    it_sup = "fa2e23c9-860a-4c90-bcc6-2c0721869a25"
    response = graphapi_post(
        """
        mutation MoveOrgUnit($uuid: UUID!, $parent: UUID!) {
          org_unit_update(
            input: {
                uuid: $uuid,
                parent: $parent,
                validity: {from: "2024-04-04"},
            }
          ) {
            uuid
          }
        }
        """,
        {
            "uuid": it_sup,
            "parent": root,
        },
    )
    assert response.errors is None

    descendant_query = """
        query DescendantQuery($from_date: DateTime, $to_date: DateTime) {
          org_units(
            filter: {
              from_date: $from_date,
              to_date: $to_date,
              descendant: {
                user_keys: "it_sup",
                from_date: $from_date,
                to_date: $to_date,
              }
            }
          ) {
            objects {
              validities {
                user_key
                uuid
                parent { uuid }
              }
            }
          }
        }
    """
    # Querying before the change should give us the original tree
    response = graphapi_post(
        descendant_query,
        {
            "from_date": "2023-03-03",
            "to_date": "2023-03-04",
        },
    )
    assert response.errors is None
    assert response.data is not None
    assert response.data["org_units"]["objects"] == [
        {
            "validities": [
                {
                    "user_key": "root",
                    "uuid": root,
                    "parent": None,
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "skole-børn",
                    "uuid": skole_born,
                    "parent": {"uuid": root},
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "it_sup",
                    "uuid": it_sup,
                    "parent": {"uuid": skole_born},
                }
            ]
        },
    ]

    # Querying after the change should give us the new tree
    response = graphapi_post(
        descendant_query,
        {
            "from_date": "2025-05-05",
            "to_date": "2025-05-06",
        },
    )
    assert response.errors is None
    assert response.data is not None
    assert response.data["org_units"]["objects"] == [
        {
            "validities": [
                {
                    "user_key": "root",
                    "uuid": root,
                    "parent": None,
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "it_sup",
                    "uuid": it_sup,
                    "parent": {"uuid": root},
                }
            ]
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_org_unit_ancestor_filter(graphapi_post: GraphAPIPost) -> None:
    """Test ancestor filter on organisation units."""
    # Ensure that the ancestor filter respects the date filtering by changing
    # the parent of 'fil' to 'it_sup' in the future: 'skole-børn > it_sup > fil'.
    root = "2874e1dc-85e6-4269-823a-e1125484dfd3"
    skole_born = "dad7d0ad-c7a9-4a94-969d-464337e31fec"
    it_sup = "fa2e23c9-860a-4c90-bcc6-2c0721869a25"
    fil = "85715fc7-925d-401b-822d-467eb4b163b6"
    response = graphapi_post(
        """
        mutation MoveOrgUnit($uuid: UUID!, $parent: UUID!) {
          org_unit_update(
            input: {
                uuid: $uuid,
                parent: $parent,
                validity: {from: "2024-04-04"},
            }
          ) {
            uuid
          }
        }
        """,
        {
            "uuid": fil,
            "parent": it_sup,
        },
    )
    assert response.errors is None

    ancestor_query = """
        query AncestorQuery($from_date: DateTime, $to_date: DateTime) {
          org_units(
            filter: {
              from_date: $from_date,
              to_date: $to_date,
              ancestor: {
                user_keys: "skole-børn",
                from_date: $from_date,
                to_date: $to_date,
              }
            }
          ) {
            objects {
              validities {
                user_key
                uuid
                parent { uuid }
              }
            }
          }
        }
    """
    # Querying before the change should give us the original descendants
    response = graphapi_post(
        ancestor_query,
        {
            "from_date": "2023-03-03",
            "to_date": "2023-03-04",
        },
    )
    assert response.errors is None
    assert response.data is not None
    assert response.data["org_units"]["objects"] == [
        {
            "validities": [
                {
                    "user_key": "skole-børn",
                    "uuid": skole_born,
                    "parent": {"uuid": root},
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "it_sup",
                    "uuid": it_sup,
                    "parent": {"uuid": skole_born},
                }
            ]
        },
    ]

    # Querying after the change should give us the new descendants
    response = graphapi_post(
        ancestor_query,
        {
            "from_date": "2025-05-05",
            "to_date": "2025-05-06",
        },
    )
    assert response.errors is None
    assert response.data is not None
    assert response.data["org_units"]["objects"] == [
        {
            "validities": [
                {
                    "user_key": "fil",
                    "uuid": fil,
                    "parent": {"uuid": it_sup},
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "skole-børn",
                    "uuid": skole_born,
                    "parent": {"uuid": root},
                }
            ]
        },
        {
            "validities": [
                {
                    "user_key": "it_sup",
                    "uuid": it_sup,
                    "parent": {"uuid": skole_born},
                }
            ]
        },
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "test_data",
    [
        {
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "user_key": "-",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "user_key": "Testing user key for tests",
            "name": "Testing name for tests",
            "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "org_unit_type": "32547559-cfc1-4d97-94c6-70b192eff825",
            "time_planning": "27935dbb-c173-4116-a4b5-75022315749d",
            "org_unit_level": "0f015b67-f250-43bb-9160-043ec19fad48",
            "org_unit_hierarchy": "89b6cef8-3d03-49ac-816f-f7530b383411",
            "validity": {"from": "2020-01-01T00:00:00+01:00", "to": None},
        },
        {
            "uuid": "dad7d0ad-c7a9-4a94-969d-464337e31fec",
            "user_key": "skole-børn",
            "name": "Skole og Børn",
            "parent": "2874e1dc-85e6-4269-823a-e1125484dfd3",
            "org_unit_type": "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
            "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
        },
    ],
)
async def test_update_org_unit_mutation_integration_test(
    graphapi_post: GraphAPIPost, test_data
) -> None:
    """Test that organisation units can be updated in LoRa via GraphQL."""
    # NOTE: A similar tests exists in test_v21.py
    #       However that test will eventually be deleted, while this should remain

    uuid = test_data["uuid"]

    query = """
        query OrgUnitQuery($uuid: UUID!) {
            org_units(filter: {uuids: [$uuid]}) {
                objects {
                    current {
                        uuid
                        user_key
                        name
                        parent: parent_uuid
                        org_unit_type: unit_type_uuid
                        time_planning: time_planning_uuid
                        org_unit_level: org_unit_level_uuid
                        org_unit_hierarchy: org_unit_hierarchy
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
    assert response.data is not None
    obj = one(response.data["org_units"]["objects"])
    assert obj["current"] is not None
    pre_update_org_unit = obj["current"]

    mutate_query = """
        mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
            org_unit_update(input: $input) {
                uuid
            }
        }
    """
    mutation_response = graphapi_post(
        mutate_query, {"input": sjsonable_encoder(test_data)}
    )
    assert mutation_response.errors is None

    response = graphapi_post(query, {"uuid": str(uuid)})
    assert response.errors is None
    assert response.data is not None
    obj = one(response.data["org_units"]["objects"])
    assert obj["current"] is not None
    post_update_org_unit = obj["current"]

    expected_updated_org_unit = {
        k: test_data.get(k) or v for k, v in pre_update_org_unit.items()
    }

    assert post_update_org_unit == expected_updated_org_unit


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "expected",
    [
        {
            "user_key": "social_og_sundhed-løn",
            "uuid": "5942ce50-2be8-476f-914b-6769a888a7c8",
            "ancestors": [
                {
                    "uuid": "b1f69701-86d8-496e-a3f1-ccef18ac1958",
                    "user_key": "løn",
                    "name": "Lønorganisation",
                    "type": "org_unit",
                    "validity": {"from": "2017-01-01T00:00:00+01:00", "to": None},
                }
            ],
        },
        {
            "user_key": "social-sundhed",
            "uuid": "68c5d78e-ae26-441f-a143-0103eca8b62a",
            "ancestors": [
                {
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "user_key": "root",
                    "name": "Overordnet Enhed",
                    "type": "org_unit",
                    "validity": {"from": "2016-01-01T00:00:00+01:00", "to": None},
                }
            ],
        },
        {
            "user_key": "fil",
            "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
            "ancestors": [
                {
                    "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                    "user_key": "hum",
                    "name": "Humanistisk fakultet",
                    "type": "org_unit",
                    "validity": {"from": "2016-12-31T00:00:00+01:00", "to": None},
                },
                {
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "user_key": "root",
                    "name": "Overordnet Enhed",
                    "type": "org_unit",
                    "validity": {"from": "2016-01-01T00:00:00+01:00", "to": None},
                },
            ],
        },
        {
            "user_key": "hum",
            "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
            "ancestors": [
                {
                    "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                    "user_key": "root",
                    "name": "Overordnet Enhed",
                    "type": "org_unit",
                    "validity": {"from": "2016-01-01T00:00:00+01:00", "to": None},
                }
            ],
        },
    ],
)
async def test_get_org_unit_ancestors(graphapi_post: GraphAPIPost, expected):
    """Tests that ancestors are properly returned on Organisation Units."""
    uuid = expected["uuid"]

    graphql_query = """
        query MyAncestorQuery($uuid: UUID!) {
          org_units(filter: {uuids: [$uuid]}) {
            objects {
              objects {
                user_key
                uuid
                ancestors {
                  uuid
                  user_key
                  name
                  type
                  validity {
                    from
                    to
                  }
                }
              }
            }
          }
        }
    """

    response = graphapi_post(query=graphql_query, variables={"uuid": str(uuid)})

    assert response.errors is None
    assert response.status_code == 200
    assert response.data is not None
    obj = one(one(response.data["org_units"]["objects"])["objects"])
    assert obj == expected
    assert len(obj) == len(expected)
    assert obj["ancestors"] == expected["ancestors"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_empty_user_key(graphapi_post: GraphAPIPost):
    """Test that org units with empty user keys can be created and read back out."""
    graphql_mutation = """
        mutation MyMutation {
          org_unit_create(
            input: {
              name: "Foo",
              user_key: "",
              org_unit_type: "4311e351-6a3c-4e7e-ae60-8a3b2938fbd6",
              validity: {from: "2012-03-04"}
            }
          ) {
            uuid
            current {
              user_key
            }
          }
        }
    """
    response = graphapi_post(query=graphql_mutation)
    assert response.errors is None
    assert response.data is not None
    assert response.data["org_unit_create"]["current"]["user_key"] == ""


fixture_parent_uuid = UUID("2874e1dc-85e6-4269-823a-e1125484dfd3")


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "initial,new,expected",
    [
        # Starting with UUID set
        # Using same UUID does nothing
        (fixture_parent_uuid, fixture_parent_uuid, fixture_parent_uuid),
        # Using unset does nothing
        (fixture_parent_uuid, UNSET, fixture_parent_uuid),
        # Using None clears the field
        (fixture_parent_uuid, None, None),
        # Starting with None
        # Using UUID sets UUID
        (None, fixture_parent_uuid, fixture_parent_uuid),
        # Using unset does nothing
        (None, UNSET, None),
        # Using None does nothing
        (None, None, None),
    ],
)
async def test_parent_changes(
    graphapi_post: GraphAPIPost,
    latest_graphql_url: str,
    initial: UUID | None,
    new: UUID | UnsetType | None,
    expected: UUID | None,
) -> None:
    """Test that we can change, noop and clear parent."""
    # NOTE: A similar tests exists in test_v21.py
    #       However that test will eventually be deleted, while this should remain
    url = latest_graphql_url

    uuid = UUID("dad7d0ad-c7a9-4a94-969d-464337e31fec")

    read_parent = partial(gen_read_parent, graphapi_post, url, uuid)
    set_parent = partial(gen_set_parent, graphapi_post, url, uuid)

    # Setup and assert initial state
    set_parent(initial)
    parent_uuid = read_parent()
    assert parent_uuid == initial

    # Fire our change and assert result
    set_parent(new)
    parent_uuid = read_parent()
    assert parent_uuid == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "children_filter",
    [
        None,
        {"from_date": None, "to_date": None},
    ],
)
async def test_has_children(
    graphapi_post: GraphAPIPost,
    children_filter: dict | None,
) -> None:
    """Test has_children works."""
    query = """
        query GetChildren(
          $children_filter: ParentBoundOrganisationUnitFilter
        ) {
          org_units(filter: { from_date: null, to_date: null }) {
            objects {
              validities(start: null, end: null) {
                children(filter: $children_filter) { uuid }
                has_children(filter: $children_filter)
              }
            }
          }
        }
    """
    response = graphapi_post(
        query,
        variables={
            "children_filter": children_filter,
        },
    )
    assert response.errors is None
    for obj in response.data["org_units"]["objects"]:
        for validity in obj["validities"]:
            assert bool(validity["children"]) == validity["has_children"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "filter,expected",
    [
        # Basics / Sanity checks
        # No filter yields all
        ({}, {"root", "l", "r", "ll", "rl", "rr"}),
        # user_key=node yields that node
        ({"user_keys": ["root"]}, {"root"}),
        ({"user_keys": ["r"]}, {"r"}),
        ({"user_keys": ["l", "r"]}, {"l", "r"}),
        # Child filter
        # Child=None yields leaves
        ({"child": None}, {"ll", "rl", "rr"}),
        # Child={} yields nodes
        ({"child": {}}, {"root", "l", "r"}),
        # Child=nodes, yields parents
        ({"child": {"user_keys": ["r"]}}, {"root"}),
        ({"child": {"user_keys": ["rl"]}}, {"r"}),
        ({"child": {"user_keys": ["l", "r"]}}, {"root"}),
        ({"child": {"user_keys": ["ll", "rl"]}}, {"l", "r"}),
        # Descendant filter
        # descendant=None or descendant={} yields all
        ({"descendant": None}, {"root", "l", "r", "ll", "rl", "rr"}),
        ({"descendant": {}}, {"root", "l", "r", "ll", "rl", "rr"}),
        # descendant=node yields ancestors
        ({"descendant": {"user_keys": ["r"]}}, {"root", "r"}),
        ({"descendant": {"user_keys": ["rl"]}}, {"root", "r", "rl"}),
        ({"descendant": {"user_keys": ["l", "r"]}}, {"root", "l", "r"}),
        ({"descendant": {"user_keys": ["ll", "rl"]}}, {"root", "l", "r", "ll", "rl"}),
        # Parent filter
        # parent=None yields roots
        ({"parent": None}, {"root"}),
        # parent={} yields non-roots
        ({"parent": {}}, {"l", "r", "ll", "rl", "rr"}),
        # parent=nodes, yields children
        ({"parent": {"user_keys": ["r"]}}, {"rl", "rr"}),
        ({"parent": {"user_keys": ["rl"]}}, set()),
        ({"parent": {"user_keys": ["l", "r"]}}, {"ll", "rl", "rr"}),
        ({"parent": {"user_keys": ["ll", "rl"]}}, set()),
        # Ancestor filter
        # ancestor=None or ancestor={} yields all
        ({"ancestor": None}, {"root", "l", "r", "ll", "rl", "rr"}),
        ({"ancestor": {}}, {"root", "l", "r", "ll", "rl", "rr"}),
        # ancestor=node yields ancestors
        ({"ancestor": {"user_keys": ["r"]}}, {"r", "rl", "rr"}),
        ({"ancestor": {"user_keys": ["rl"]}}, {"rl"}),
        ({"ancestor": {"user_keys": ["l", "r"]}}, {"l", "r", "ll", "rl", "rr"}),
        ({"ancestor": {"user_keys": ["ll", "rl"]}}, {"ll", "rl"}),
        # Combined filters
        # child={}, parent={} yields non-root nodes
        ({"child": {}, "parent": {}}, {"r", "l"}),
        # child=None, parent=None yields all childless roots
        ({"child": None, "parent": None}, set()),
        # child={}, parent=None yields all roots with children
        ({"child": {}, "parent": None}, {"root"}),
        # child=None, parent={} yields all non-root leaves
        ({"child": None, "parent": {}}, {"ll", "rl", "rr"}),
        # ancestor=r, descendant=r yields r
        ({"descendant": {"user_keys": ["r"]}, "ancestor": {"user_keys": ["r"]}}, {"r"}),
    ],
)
async def test_org_tree_filters(
    graphapi_post: GraphAPIPost,
    filter: dict[str, dict[str, list[str]] | None],
    expected: set[str],
) -> None:
    """Test the various org-unit tree filters work as expected.

    Args:
        graphapi_post: The GraphQL client to run our query with.
        filter: The GraphQL filter to apply to our org-unit query.
        expected: The set of user-keys we expected to get back.
    """

    async def create_org() -> UUID:
        mutate_query = """
            mutation CreateOrg($input: OrganisationCreate!) {
                org_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query, variables={"input": {"municipality_code": None}}
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["org_create"]["uuid"])

    async def create_org_unit(user_key: str, parent: UUID | None = None) -> UUID:
        mutate_query = """
            mutation CreateOrgUnit($input: OrganisationUnitCreateInput!) {
                org_unit_create(input: $input) {
                    uuid
                }
            }
        """
        response = graphapi_post(
            query=mutate_query,
            variables={
                "input": {
                    "name": user_key,
                    "user_key": user_key,
                    "parent": str(parent) if parent else None,
                    "validity": {"from": "1970-01-01T00:00:00Z"},
                    "org_unit_type": str(uuid4()),
                }
            },
        )
        assert response.errors is None
        assert response.data
        return UUID(response.data["org_unit_create"]["uuid"])

    await create_org()

    # Construct our test-tree
    #     root
    #     / \
    #    l   r
    #   /   / \
    # ll   rl  rr
    root = await create_org_unit("root")
    left = await create_org_unit("l", root)
    await create_org_unit("ll", left)
    right = await create_org_unit("r", root)
    await create_org_unit("rl", right)
    await create_org_unit("rr", right)

    # Test our filter
    query = """
        query TestOrgUnitTreeFilters(
          $filter: OrganisationUnitFilter
        ) {
          org_units(filter: $filter) {
            objects {
              current {
                user_key
              }
            }
          }
        }
    """
    response = graphapi_post(query, variables={"filter": filter})
    assert response.errors is None
    assert response.data
    results = {
        x["current"]["user_key"]
        for x in response.data["org_units"]["objects"]
        if x["current"] is not None
    }
    assert results == expected

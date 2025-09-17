# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid
from datetime import datetime
from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

from mora.config import Settings
from mora.service.autocomplete.employees import decorate_employee_search_result
from mora.service.autocomplete.orgunits import decorate_orgunit_search_result
from mora.service.autocomplete.orgunits import search_orgunits


@patch("mora.service.autocomplete.get_results")
@patch("mora.service.orgunit.config.get_settings")
def test_v2_legacy_logic(mock_get_settings, mock_get_results, service_client) -> None:
    class_uuids = [
        uuid.UUID("e8ea1a09-d3d4-4203-bfe9-d9a213371337"),
    ]

    mock_get_settings.return_value = MagicMock(
        confdb_autocomplete_v2_use_legacy=True,
        confdb_autocomplete_attrs_orgunit=class_uuids,
    )
    mock_get_results.return_value = {"items": []}

    at = datetime.now().date()
    query = "f494ad89-039d-478e-91f2-a63566554666"
    response = service_client.request(
        "GET", f"/service/ou/autocomplete/?query={query}&at={at.isoformat()}"
    )

    assert response.status_code == 200
    mock_get_results.assert_called()
    mock_get_results.assert_called_with(ANY, class_uuids, query)


# ORG UNITS


@patch("mora.service.autocomplete.orgunits.execute_graphql", new_callable=AsyncMock)
async def test_v2_decorate_orgunits(mock_execute_graphql):
    test_data = {
        "uuid": "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
        "name": "Viuf skole",
        "user_key": "Viuf skole",
        "validity": {"from": "1960-01-01T00:00:00+01:00", "to": None},
        "ancestors_validity": [
            {"name": "Skoler og børnehaver"},
            {"name": "Skole og Børn"},
            {"name": "Kolding Kommune"},
        ],
    }

    expected_result = [
        {
            "uuid": uuid.UUID(test_data["uuid"]),
            "name": test_data["name"],
            "path": [
                # [::-1] reverses the list
                ancestor["name"]
                for ancestor in test_data["ancestors_validity"][::-1]
            ]
            + [test_data["name"]],
            "attrs": [],
            "validity": test_data["validity"],
        }
    ]

    mock_execute_graphql.return_value = MagicMock(
        data={
            "org_units": {
                "objects": [
                    {
                        "uuid": test_data["uuid"],
                        "current": test_data,
                        "objects": [test_data],
                    }
                ]
            }
        },
        errors=None,
    )

    # Invoke
    now = datetime.now()
    result = await decorate_orgunit_search_result(
        settings=MagicMock(confdb_autocomplete_attrs_orgunit=None),
        search_results=[uuid.UUID(test_data["uuid"])],
        at=now.date(),
    )

    # Asserts
    mock_execute_graphql.assert_called_with(
        ANY,
        variable_values={
            "uuids": [test_data["uuid"]],
            "from_date": now.date().isoformat(),
        },
    )

    assert result == expected_result


@patch("mora.service.autocomplete.orgunits.execute_graphql", new_callable=AsyncMock)
async def test_v2_decorate_orgunits_attrs(mock_execute_graphql):
    test_data = {
        "uuid": "08eaf849-e9f9-53e0-b6b9-3cd45763ecbb",
        "name": "Viuf skole",
        "user_key": "Viuf skole",
        "validity": {"from": "1960-01-01T00:00:00+01:00", "to": None},
        "ancestors_validity": [
            {"name": "Skoler og børnehaver"},
            {"name": "Skole og Børn"},
            {"name": "Kolding Kommune"},
        ],
        "addresses": [
            {
                "uuid": "279a900a-a1a6-4c93-9c58-4f7d31108cdd",
                "name": "Viuf_skole@kolding.dk",
                "address_type": {
                    "uuid": "61c22b75-01b0-4e83-954c-9cf0c8dc79fe",
                    "name": "Email",
                },
            },
            {
                "uuid": "b756c0c9-75b7-4ed3-a731-b66946b09437",
                "name": "Næsbyvej 26, 6000 Kolding",
                "address_type": {
                    "uuid": "5260d4aa-e33b-48f7-ae3e-6074262cbdcf",
                    "name": "Postadresse",
                },
            },
        ],
        "itusers": [
            {
                "uuid": "397c3967-fb29-425a-88a5-dac2c804cbab",
                "user_key": "viuf-skole-test-ad",
                "itsystem": {
                    "uuid": "a1608e69-c422-404f-a6cc-b873c50af111",
                    "user_key": "Active Directory",
                    "name": "Active Directory",
                },
            }
        ],
    }

    # Configure expected result from test data
    expected_attrs = []
    for addr in test_data["addresses"]:
        expected_attrs.append(
            {
                "uuid": uuid.UUID(addr["uuid"]),
                "value": addr["name"],
                "title": addr["address_type"]["name"],
            }
        )

    for ituser in test_data["itusers"]:
        expected_attrs.append(
            {
                "uuid": uuid.UUID(ituser["uuid"]),
                "value": ituser["user_key"],
                "title": ituser["itsystem"]["name"],
            }
        )

    expected_result = [
        {
            "uuid": uuid.UUID(test_data["uuid"]),
            "name": test_data["name"],
            "path": [
                # [::-1] reverses the list
                ancestor["name"]
                for ancestor in test_data["ancestors_validity"][::-1]
            ]
            + [test_data["name"]],
            "attrs": expected_attrs,
            "validity": test_data["validity"],
        }
    ]

    # Mock GraphQL response & Invoke
    mock_execute_graphql.return_value = MagicMock(
        data={
            "org_units": {
                "objects": [
                    {
                        "uuid": test_data["uuid"],
                        "current": test_data,
                        "objects": [test_data],
                    }
                ]
            }
        },
        errors=None,
    )

    now = datetime.now()
    result = await decorate_orgunit_search_result(
        settings=Settings(
            confdb_autocomplete_attrs_orgunit=[
                uuid.UUID(test_data["addresses"][0]["address_type"]["uuid"]),
                uuid.UUID(test_data["addresses"][1]["address_type"]["uuid"]),
                uuid.UUID(test_data["itusers"][0]["itsystem"]["uuid"]),
            ]
        ),
        search_results=[uuid.UUID(test_data["uuid"])],
        at=now.date(),
    )

    # Asserts
    mock_execute_graphql.assert_called_with(
        ANY,
        variable_values={
            "uuids": [test_data["uuid"]],
            "from_date": now.date().isoformat(),
        },
    )

    assert result == expected_result


@patch("mora.service.autocomplete.orgunits._sqlalchemy_generate_query")
async def test_v2_search_orgunits(mock_sqlalchemy_generate_query):
    """Test that search_orgunits() returns the expected result

    NOTE: The unit test does not patch out read_sqlalchemy_result(), but
    instead mocks the sqlalchemy result.
    """

    search_query = "Samfundsvidenskabelige"
    expected = [uuid.UUID("b688513d-11f7-4efc-b679-ab082a2055d0")]

    # Mocking
    mock_sqlalchemy_generate_query.return_value = "some-verification-return"

    session_mock = MagicMock()

    # NOTE: 1000 is the default chunk size of read_sqlalchemy_result()
    sqlalchemy_result_chunck_size = 1000
    sqlalchemy_fetchmany_rows_mocked = [MagicMock(uuid=uuid) for uuid in expected]
    sqlalchemy_fetchmany_mock_return = [
        sqlalchemy_fetchmany_rows_mocked[i : i + sqlalchemy_result_chunck_size]
        for i in range(
            0, len(sqlalchemy_fetchmany_rows_mocked), sqlalchemy_result_chunck_size
        )
    ]
    sqlalchemy_fetchmany_mock_return.append([])

    session_mock.execute = AsyncMock(
        return_value=MagicMock(  # sqlalchemy result
            fetchmany=MagicMock(  # sqlalchemy rows
                side_effect=sqlalchemy_fetchmany_mock_return,
            )
        )
    )

    # Invoke search_orgunits with mocked sessionmaker
    result = await search_orgunits(session_mock, search_query)

    # Asserts
    mock_sqlalchemy_generate_query.assert_called_with(search_query, ANY)
    session_mock.execute.assert_called_with(
        mock_sqlalchemy_generate_query.return_value, {}
    )
    assert result == expected


# EMPLOYEES


@patch("mora.service.autocomplete.employees.execute_graphql", new_callable=AsyncMock)
async def test_v2_decorate_employees(mock_execute_graphql):
    test_data = {
        "uuid": "82a728b4-b7d0-40ea-a3db-8dbbf911a3e6",
        "user_key": "AllanO",
        "cpr_no": "0501402419",
        "name": "Allan Bastrup Odgaard",
        "givenname": "Allan Bastrup",
        "surname": "Odgaard",
        "nickname": "",
        "nickname_givenname": "",
        "nickname_surname": "",
        "validity": {"from": "1940-01-05T00:00:00+01:00", "to": None},
        "engagements": [
            {
                "uuid": "3fea2351-dad8-4f7f-8c2b-5d73d83f51b1",
                "user_key": "-",
                "engagement_type": {
                    "uuid": "8acc5743-044b-4c82-9bb9-4e572d82b524",
                    "name": "Ansat",
                    "published": "Publiceret",
                },
            }
        ],
        "addresses": [
            {
                "uuid": "5d60f62e-f17e-4b85-990f-42136eb19cd0",
                "user_key": "53103758",
                "value": "53103758",
                "address_type": {
                    "uuid": "05b69443-0c9f-4d57-bb4b-a8c719afff89",
                    "name": "Telefon",
                    "published": "Publiceret",
                },
            },
            {
                "uuid": "9a4aeebc-8fff-49eb-9f9b-02f3c3a4f0ce",
                "user_key": "allano@kolding.dk",
                "value": "allano@kolding.dk",
                "address_type": {
                    "uuid": "f376deb8-4743-4ca6-a047-3241de8fe9d2",
                    "name": "Email",
                    "published": "Publiceret",
                },
            },
            {
                "uuid": "9f87c7f5-2e1c-45df-8a23-f6157a2ae2db",
                "user_key": "0a3f50bc-35ff-32b8-e044-0003ba298018",
                "value": "0a3f50bc-35ff-32b8-e044-0003ba298018",
                "address_type": {
                    "uuid": "e75f74f5-cbc4-4661-b9f4-e6a9e05abb2d",
                    "name": "Postadresse",
                    "published": "Publiceret",
                },
            },
        ],
        "associations": [
            {
                "uuid": "3e45aeb0-29a6-41b9-8d04-1a50619b3076",
                "user_key": "-",
                "association_type": {
                    "uuid": "cc42af04-55f5-4483-87c3-3a22d8003d7e",
                    "name": "Leder",
                    "published": "Publiceret",
                },
            }
        ],
        "itusers": [
            {
                "uuid": "e748df8f-dba4-494b-a3a1-9bccebc27538",
                "user_key": "AllanO",
                "itsystem": {
                    "uuid": "5168dd45-4cb5-4932-b8a1-10dbe736fc5d",
                    "name": "Office365",
                },
            }
        ],
    }

    # mocking
    mock_execute_graphql.return_value = MagicMock(
        data={
            "employees": {
                "objects": [
                    {
                        "uuid": test_data["uuid"],
                        "current": test_data,
                        "objects": [test_data],
                    }
                ]
            }
        },
        errors=None,
    )

    # invoke
    result = await decorate_employee_search_result(
        settings=Settings(
            confdb_autocomplete_attrs_employee=[
                uuid.UUID(
                    test_data["engagements"][0]["engagement_type"]["uuid"]
                ),  # engagement_type = Ansat
                uuid.UUID(
                    test_data["addresses"][0]["address_type"]["uuid"]
                ),  # address_type = Email
                uuid.UUID(
                    test_data["associations"][0]["association_type"]["uuid"]
                ),  # association_type = Medlem
                uuid.UUID(
                    test_data["itusers"][0]["itsystem"]["uuid"]
                ),  # itsystem = Active Directory
                uuid.UUID("14466fb0-f9de-439c-a6c2-b3262c367da7"),  # itsystem = SAP
            ],
        ),
        search_results=[uuid.UUID(test_data["uuid"])],
        at=None,
    )

    # assert
    assert result == [
        {
            "uuid": uuid.UUID(test_data["uuid"]),
            "name": test_data["name"],
            "attrs": [
                {
                    "uuid": uuid.UUID("5d60f62e-f17e-4b85-990f-42136eb19cd0"),
                    "title": "Telefon",
                    "value": "53103758",
                },
                {
                    "uuid": uuid.UUID("e748df8f-dba4-494b-a3a1-9bccebc27538"),
                    "title": "Office365",
                    "value": "AllanO",
                },
            ],
        }
    ]

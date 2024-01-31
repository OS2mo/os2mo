# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from more_itertools import one

from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
@pytest.mark.parametrize(
    "resolver,filter_uuid,expected_user_key",
    [
        (
            "addresses",
            "414044e0-fe5f-4f82-be20-1e107ad50e80",
            "Nordre Ringgade 1, 8000 Aarhus C",
        ),
        ("associations", "c2153d5d-4a2b-492d-a18c-c498f7bb6221", "bvn"),
        ("classes", "06f95678-166a-455a-a2ab-121a8d92ea23", "ansat"),
        ("employees", "236e0a78-11a0-4ed9-8545-6286bb8611c7", "eriksmidthansen"),
        ("engagements", "301a906b-ef51-4d5c-9c77-386fb8410459", "bvn"),
        ("facets", "1a6045a2-7a8e-4916-ab27-b2402e64f2be", "engagement_job_function"),
        ("itsystems", "59c135c9-2b15-41cc-97c8-b5dff7180beb", "AD"),
        (
            "itusers",
            "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
            "18d2271a-45c4-406c-a482-04ab12f80881",
        ),
        ("kles", "4bee0127-a3a3-419a-8bcc-d1b81d21c5b5", "1234"),
        ("leaves", "0895b7f5-86ac-45c5-8fb1-c3047d45b643", "bvn"),
        (
            "managers",
            "05609702-977f-4869-9fb4-50ad74c6999a",
            "be736ee5-5c44-4ed9-b4a4-15ffa19e2848",
        ),
        ("org_units", "5942ce50-2be8-476f-914b-6769a888a7c8", "social_og_sundhed-løn"),
        (
            "owners",
            "c16ff527-3501-42f7-a942-e606c6c1a0a7",
            "f2b92485-2564-41c4-8f0d-3e09190253aa",
        ),
        ("related_units", "5c68402c-2a8d-4776-9237-16349fc72648", "rod <-> hum"),
        ("roles", "1b20d0b9-96a0-42a6-b196-293bb86e62e8", "bvn"),
    ],
)
async def test_top_level_resolver_uuid_filters(
    graphapi_post: GraphAPIPost, resolver: str, filter_uuid: str, expected_user_key: str
) -> None:
    """Test top-level resolver filters."""
    query = f"""
        query TestTopLevelResolversQuery {{
          {resolver}(uuids: "{filter_uuid}") {{
            objects {{
              current {{
                user_key
              }}
            }}
          }}
        }}
    """
    response = graphapi_post(query, url="/graphql/v13")
    assert response.errors is None
    objects = one(response.data.values())["objects"]
    assert one(objects)["current"]["user_key"] == expected_user_key


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_configuration_resolver_filters(graphapi_post: GraphAPIPost) -> None:
    """Test configuration resolver filters."""
    query = """
        query TestConfigurationResolver {
          configuration(identifiers: "foo") {
            objects {
              key
            }
          }
        }
    """
    response = graphapi_post(query, url="/graphql/v13")
    assert response.errors is None


@pytest.mark.xfail(reason="waiting for #58757")
@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_files_resolver_filters(graphapi_post: GraphAPIPost) -> None:
    """Test files resolver filters."""
    query = """
        query TestFilesResolver {
          files(file_store: EXPORTS, file_names: "foo") {
            objects {
              base64_contents
            }
          }
        }
    """
    response = graphapi_post(query, url="/graphql/v13")
    assert response.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_healths_resolver_fclearilters(graphapi_post: GraphAPIPost) -> None:
    """Test healths resolver filters."""
    query = """
        query TestHealthsResolver {
          configuration(identifiers: "foo") {
            objects {
              key
            }
          }
        }
    """
    response = graphapi_post(query, url="/graphql/v13")
    assert response.errors is None


@pytest.mark.integration_test
@pytest.mark.usefixtures("load_fixture_data_with_reset")
async def test_nested_resolver_filters(graphapi_post: GraphAPIPost) -> None:
    """Test nested resolver filters."""
    query = """
        query TestNestedLevelResolversQuery {
          org_units(user_keys: "hum") {
            objects {
              current {
                uuid
                user_key
                engagements(uuids: "d000591f-8705-4324-897a-075e3623f37b") {
                  uuid
                  user_key
                  person(cpr_numbers: "0906340000") {
                    uuid
                    user_key
                    cpr_number
                  }
                }
              }
            }
          }
        }
    """
    response = graphapi_post(query, url="/graphql/v13")
    assert response.errors is None
    assert response.data == {
        "org_units": {
            "objects": [
                {
                    "current": {
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "user_key": "hum",
                        "engagements": [
                            {
                                "uuid": "d000591f-8705-4324-897a-075e3623f37b",
                                "user_key": "bvn",
                                "person": [
                                    {
                                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                                        "user_key": "andersand",
                                        "cpr_number": "0906340000",
                                    }
                                ],
                            }
                        ],
                    }
                }
            ]
        }
    }

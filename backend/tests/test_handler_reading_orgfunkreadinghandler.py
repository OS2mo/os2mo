# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from mora.handler.reading import OrgFunkReadingHandler
from mora.lora import Connector

UNIT_UUID = "2874e1dc-85e6-4269-823a-e1125484dfd3"


@pytest.fixture(scope="session")
def lora_connector() -> Connector:
    return Connector(virkningfra="-infinity", virkningtil="infinity")


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_get_search_fields() -> None:
    result = OrgFunkReadingHandler._get_search_fields("ou", UNIT_UUID)
    assert result == {OrgFunkReadingHandler.SEARCH_FIELDS["ou"]: UNIT_UUID}


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_get_from_type(lora_connector: Connector) -> None:
    result = await OrgFunkReadingHandler.get_from_type(lora_connector, "ou", UNIT_UUID)
    assert isinstance(result, list)
    assert {item["user_key"] for item in result} == {
        "rod <-> fil",
        "rod <-> hum",
        "Nordre Ringgade 1, 8000 Aarhus C",
    }


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_get_count(lora_connector: Connector) -> None:
    # This counts the 2 org funcs of type "tilknyttedeenheder"
    # ("rod <-> fil", "rod <-> hum")
    result = await OrgFunkReadingHandler.get_count(lora_connector, "ou", UNIT_UUID)
    assert result == 3

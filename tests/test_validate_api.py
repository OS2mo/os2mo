# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock
from unittest.mock import patch

from mora import util as mora_util

UUID = {"uuid": "be0df80c-7eed-4a2e-a682-e36be4e4877e"}
FROM_DATE = "2000-01-01"
PERSON_UUID = "cc1fc948-d3f6-4bbc-9faf-288e0f956135"
ORG_UNIT_UUID = "f4f28810-cdd9-4ff5-821e-427378ab4bf7"


@patch("mora.service.address_handler.base.get_handler_for_scope")
@patch("mora.service.facet.get_one_class")
def test_address(get_one_class, get_handler_for_scope, service_client):
    value = "12341234"
    scope = "SCOPE"

    payload = {
        "address_type": {"uuid": "cc1fc948-d3f6-4bbc-9faf-288e0f956135"},
        "value": value,
    }
    get_one_class.return_value = {"scope": scope}
    get_handler_for_scope.return_value = handler = AsyncMock()

    service_client.request("POST", "/service/validate/address/", json=payload)

    get_handler_for_scope.assert_called_with(scope)
    handler.validate_value.assert_called_with(value)

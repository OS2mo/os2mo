# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient
from mora import lora
from mora.auth.middleware import LORA_USER_UUID


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
async def test_register_brugerref(
    raw_client: TestClient, auth_headers: dict[str, str]
) -> None:
    # Create a user using a raw client and our JWT token
    payload = {
        "givenname": "Torkild",
        "surname": "von Testperson",
        "nickname_givenname": "Torkild",
        "nickname_surname": "Sejfyr",
        "seniority": "2017-01-01",
        "cpr_no": "0101501234",
        "org": {"uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"},
    }
    response = raw_client.post("/service/e/create", json=payload, headers=auth_headers)
    assert response.status_code == 201
    userid = response.json()

    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")
    actual = await c.bruger.get(userid)
    assert actual is not None

    # We expect the userref to be set to the uuid from the JWT token
    userref = actual["brugerref"]
    assert userref == "99e7b256-7dfa-4ee8-95c6-e3abe82e236a"
    assert userref != str(LORA_USER_UUID)

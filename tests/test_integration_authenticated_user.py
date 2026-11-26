# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from mora import lora
from mora.auth.middleware import LORA_USER_UUID
from mora.db import Actor
from mora.db import AsyncSession


@pytest.mark.integration_test
async def test_register_brugerref(
    fixture_db: AsyncSession, raw_client: TestClient, auth_headers: dict[str, str]
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

    # We expect the userref to be set to the actor of the JWT token's username
    actor = await fixture_db.scalar(
        select(Actor.uuid).where(Actor.username == "alvida")
    )
    userref = actual["brugerref"]
    assert userref == str(actor)
    assert userref != str(LORA_USER_UUID)

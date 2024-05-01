# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from unittest.mock import ANY
from unittest.mock import MagicMock
from unittest.mock import patch
from uuid import uuid4

import pytest
from ldap3 import BASE
from ldap3 import Connection
from ldap3 import MOCK_SYNC
from ldap3 import SUBTREE
from more_itertools import one

from mo_ldap_import_export.config import Settings
from mo_ldap_import_export.ldap import configure_ldap_connection
from mo_ldap_import_export.ldap import construct_server_pool


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    # Mapping
    monkeypatch.setenv(
        "CONVERSION_MAPPING",
        '{"ldap_to_mo": {}, "mo_to_ldap": {}, "username_generator": {}}',
    )
    # MO
    monkeypatch.setenv("CLIENT_ID", "foo")
    monkeypatch.setenv("CLIENT_SECRET", "bar")
    # LDAP
    monkeypatch.setenv("LDAP_CONTROLLERS", '[{"host": "0.0.0.0"}]')
    monkeypatch.setenv("LDAP_DOMAIN", "example.com")
    monkeypatch.setenv("LDAP_USER", "foo")
    monkeypatch.setenv("LDAP_PASSWORD", "bar")
    monkeypatch.setenv("LDAP_SEARCH_BASE", "dc=example,dc=com")
    monkeypatch.setenv("LDAP_AUTH_METHOD", "simple")
    # Misc
    monkeypatch.setenv("DEFAULT_ORG_UNIT_LEVEL", "foo")
    monkeypatch.setenv("DEFAULT_ORG_UNIT_TYPE", "foo")
    # AMQP
    monkeypatch.setenv("FASTRAMQPI__AMQP__URL", "amqp://guest:guest@msg_broker:5672/")
    monkeypatch.setenv("INTERNAL_AMQP__URL", "amqp://guest:guest@msg_broker:5672/")

    return Settings()


@pytest.fixture
def ldap_container_dn() -> str:
    return "o=example"


@pytest.fixture
def ldap_connection(settings: Settings, ldap_container_dn: str) -> Iterable[Connection]:
    """Fixture to construct a mocked ldap_connection.

    Returns:
        The mocked ldap_connection.
    """
    # See https://ldap3.readthedocs.io/en/latest/mocking.html for details
    with patch(
        "mo_ldap_import_export.ldap.get_client_strategy", return_value=MOCK_SYNC
    ):
        # This patch is necessary due to: https://github.com/cannatag/ldap3/issues/1007
        server = one(construct_server_pool(settings).servers)
        with patch(
            "mo_ldap_import_export.ldap.construct_server_pool", return_value=server
        ):
            ldap_connection = configure_ldap_connection(settings)
            ldap_connection.strategy.add_entry(
                f"CN={settings.ldap_user},{ldap_container_dn}",
                {
                    "objectClass": "inetOrgPerson",
                    "userPassword": settings.ldap_password.get_secret_value(),
                    "sn": f"{settings.ldap_user}_sn",
                    "revision": 0,
                },
            )
            ldap_connection.bind()
            yield ldap_connection


async def test_searching_mocked(
    ldap_connection: MagicMock, settings: Settings, ldap_container_dn: str
) -> None:
    """Test that we can use the mocked ldap_connection to search for our default user."""
    ldap_connection.search(
        ldap_container_dn,
        f"(cn={settings.ldap_user})",
        search_scope=SUBTREE,
        attributes="*",
    )
    assert ldap_connection.result["description"] == "success"

    search_result = one(ldap_connection.response)
    assert search_result == {
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "userPassword": [settings.ldap_password.get_secret_value()],
            "sn": [f"{settings.ldap_user}_sn"],
            "revision": ["0"],
            "CN": [settings.ldap_user],
        },
        "dn": f"CN={settings.ldap_user},{ldap_container_dn}",
        "raw_attributes": ANY,
        "raw_dn": ANY,
        "type": "searchResEntry",
    }


async def test_searching_newly_added(ldap_connection: MagicMock) -> None:
    """Test that we can use the mocked ldap_connection to find newly added users."""
    username = str(uuid4())
    password = str(uuid4())
    container = str(uuid4())
    # Add new entry
    ldap_connection.strategy.add_entry(
        f"cn={username},o={container}",
        {
            "objectClass": "inetOrgPerson",
            "userPassword": password,
            "sn": f"{username}_sn",
            "revision": 1,
        },
    )

    ldap_connection.search(
        f"o={container}", f"(cn={username})", search_scope=SUBTREE, attributes="*"
    )
    assert ldap_connection.result["description"] == "success"

    search_result = one(ldap_connection.response)
    assert search_result == {
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "userPassword": [password],
            "sn": [f"{username}_sn"],
            "revision": ["1"],
            "CN": [username],
        },
        "dn": f"cn={username},o={container}",
        "raw_attributes": ANY,
        "raw_dn": ANY,
        "type": "searchResEntry",
    }


async def test_searching_dn_lookup(
    ldap_connection: MagicMock, settings: Settings, ldap_container_dn: str
) -> None:
    """Test that we can read our default user."""
    dn = f"CN={settings.ldap_user},{ldap_container_dn}"
    ldap_connection.search(
        dn,
        "(objectclass=*)",
        attributes="*",
        search_scope=BASE,
    )
    assert ldap_connection.result["description"] == "success"

    search_result = one(ldap_connection.response)
    assert search_result == {
        "attributes": {
            "objectClass": ["inetOrgPerson"],
            "userPassword": [settings.ldap_password.get_secret_value()],
            "sn": [f"{settings.ldap_user}_sn"],
            "revision": ["0"],
            "CN": [settings.ldap_user],
        },
        "dn": f"CN={settings.ldap_user},{ldap_container_dn}",
        "raw_attributes": ANY,
        "raw_dn": ANY,
        "type": "searchResEntry",
    }

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import AsyncMock

import pytest
from ldap3 import Connection

from mo_ldap_import_export.depends import Settings
from mo_ldap_import_export.ldap import filter_dns
from mo_ldap_import_export.types import DN
from mo_ldap_import_export.utils import combine_dn_strings
from tests.integration.conftest import AddLdapPerson


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.parametrize("input_dns", [set(), {"CN=foo"}, {"CN=foo", "CN=bar"}])
async def test_filter_dns_no_filter(input_dns: set[DN]) -> None:
    ldap_connection = AsyncMock()

    settings = Settings()
    assert settings.discriminator_filter is None

    output_dns = await filter_dns(settings, ldap_connection, input_dns)
    assert input_dns == output_dns


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_filter_dns_no_fields() -> None:
    ldap_connection = AsyncMock()

    settings = Settings()
    assert settings.discriminator_filter is None
    settings = settings.copy(update={"discriminator_filter": "True"})
    assert settings.discriminator_filter == "True"

    with pytest.raises(AssertionError) as exc_info:
        await filter_dns(settings, ldap_connection, {"CN=foo"})
    assert "discriminator_fields must be set" in str(exc_info.value)


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "True",
        "DISCRIMINATOR_VALUES": '["True"]',
        "DISCRIMINATOR_FIELDS": '["title"]',
    }
)
@pytest.mark.parametrize(
    "filtered",
    [
        # Filter always rejects
        pytest.param(True, marks=pytest.mark.envvar({"DISCRIMINATOR_FILTER": "False"})),
        # Filter always accepts
        pytest.param(False, marks=pytest.mark.envvar({"DISCRIMINATOR_FILTER": "True"})),
        # Filter accepts if title is correct (using value)
        pytest.param(
            False,
            marks=pytest.mark.envvar(
                {"DISCRIMINATOR_FILTER": '{{ value == "Skole underviser" }}'}
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.envvar(
                {"DISCRIMINATOR_FILTER": '{{ value == "Software udvikler" }}'}
            ),
        ),
        # Filter accepts if substring in title is found (using title)
        pytest.param(
            False,
            marks=pytest.mark.envvar(
                {"DISCRIMINATOR_FILTER": '{{ "Skole" in title }}'}
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.envvar(
                {"DISCRIMINATOR_FILTER": '{{ "Software" in title }}'}
            ),
        ),
    ],
)
async def test_filter_dns(
    ldap_connection: Connection, ldap_person_dn: DN, filtered: bool
) -> None:
    settings = Settings()
    result = await filter_dns(settings, ldap_connection, {ldap_person_dn})
    expected = set() if filtered else {ldap_person_dn}
    assert result == expected


@pytest.mark.integration_test
@pytest.mark.envvar(
    {
        "LISTEN_TO_CHANGES_IN_MO": "False",
        "LISTEN_TO_CHANGES_IN_LDAP": "True",
        "DISCRIMINATOR_VALUES": '["True"]',
        "DISCRIMINATOR_FIELDS": '["employeeNumber"]',
        # Only accept users born before the moon landing (by date)
        "DISCRIMINATOR_FILTER": """
        {% set number = value|int %}
        {% set rest = (number / 10000)|int %}
        {% set code = number % 10000 %}

        {% set year = rest % 100 %}
        {% set rest = (rest / 100)|int %}

        {% set month = rest % 100 %}
        {% set rest = (rest / 100)|int %}

        {% set day = rest % 100 %}
        {% set rest = (rest / 100)|int %}

        {% if rest %}
            Invalid CPR number: {{ value }}
        {% endif %}

        {% if code < 4000 %}
            {% set century = 1900 %}
        {% elif code < 5000 %}
            {% set century = 2000 if year <= 36 else 1900 %}
        {% elif code < 9000 %}
            {% set century = 2000 if year <= 57 else 1800 %}
        {% else %}
            {% set century = 2000 if year <= 36 else 1900 %}
        {% endif %}

        {% set year = century + year %}
        {{ year < 1969 or (year <= 1969 and month <= 7 and day <= 20) }}
        """,
    }
)
async def test_filter_dns_accepts_pre_moonlanding(
    ldap_connection: Connection, add_ldap_person: AddLdapPerson
) -> None:
    # Born 24th of December 1885
    b18 = combine_dn_strings(await add_ldap_person("b18", "2412855038"))
    # Born 18th of July 1969
    b19 = combine_dn_strings(await add_ldap_person("b19", "1907690004"))
    # Born 21st of July 1969
    a19 = combine_dn_strings(await add_ldap_person("a19", "2107690002"))
    # Born 11th of September 2001
    a20 = combine_dn_strings(await add_ldap_person("a20", "1109014008"))

    # Check that only b18 and b19 survives our filter
    settings = Settings()
    result = await filter_dns(settings, ldap_connection, {b18, b19, a19, a20})
    assert result == {b18, b19}

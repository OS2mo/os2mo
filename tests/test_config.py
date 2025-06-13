# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
import pathlib
from functools import partial
from typing import Any
from typing import cast
from unittest.mock import patch

import pytest
from mergedeep import Strategy  # type: ignore
from mergedeep import merge  # type: ignore
from more_itertools import one
from pydantic import ValidationError
from pydantic import parse_obj_as
from pydantic.env_settings import SettingsError

from mo_ldap_import_export.config import ConversionMapping
from mo_ldap_import_export.config import JinjaTemplate
from mo_ldap_import_export.config import LDAP2MOMapping
from mo_ldap_import_export.config import Settings

overlay = partial(merge, strategy=Strategy.TYPESAFE_ADDITIVE)


@pytest.fixture
def address_mapping(minimal_mapping: dict) -> dict:
    new_mapping = overlay(
        minimal_mapping,
        {
            "ldap_to_mo": {
                "EmailEmployee": {
                    "objectClass": "Address",
                    "_import_to_mo_": "true",
                    "_ldap_attributes_": ["mail"],
                    "value": "{{ldap.mail or ''}}",
                    "address_type": "{{ get_employee_address_type_uuid('EmailEmployee') }}",
                    "person": "{{ employee_uuid or '' }}",
                }
            }
        },
    )
    return cast(dict, new_mapping)


def test_minimal_config(minimal_mapping: dict) -> None:
    """Happy path test for the minimal acceptable mapping."""
    conversion_mapping = parse_obj_as(ConversionMapping, minimal_mapping)
    assert conversion_mapping.dict(exclude_unset=True, by_alias=True) == minimal_mapping


def test_address_config(address_mapping: dict) -> None:
    """Happy path test for the address  mapping."""
    conversion_mapping = parse_obj_as(ConversionMapping, address_mapping)
    assert conversion_mapping.dict(exclude_unset=True, by_alias=True) == address_mapping


def test_cannot_terminate_employee(minimal_mapping: dict) -> None:
    """Test that employees cannot be terminated."""
    invalid_mapping = overlay(
        minimal_mapping,
        {
            "ldap_to_mo": {
                "Employee": {
                    "objectClass": "Employee",
                    "_import_to_mo_": "false",
                    "_ldap_attributes_": ["employeeID"],
                    "_terminate_": "whatever",
                    "cpr_number": "{{ldap.employeeID or None}}",
                    "uuid": "{{ employee_uuid or '' }}",
                }
            }
        },
    )
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(ConversionMapping, invalid_mapping)
    assert "Termination not supported for employee" in str(exc_info.value)


def test_can_terminate_address(address_mapping: dict) -> None:
    """Test that addresses can be terminated."""
    new_mapping = overlay(
        address_mapping,
        {
            "ldap_to_mo": {
                "EmailEmployee": {"_terminate_": "whatever", "uuid": "whatever"}
            },
        },
    )
    parse_obj_as(ConversionMapping, new_mapping)


def test_terminate_address_no_uuid(address_mapping: dict) -> None:
    new_mapping = overlay(
        address_mapping,
        {
            "ldap_to_mo": {"EmailEmployee": {"_terminate_": "whatever"}},
        },
    )
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(ConversionMapping, new_mapping)
    assert "UUID must be set if _terminate_ is set" in str(exc_info.value)


def test_terminate_address_empty_uuid(address_mapping: dict) -> None:
    new_mapping = overlay(
        address_mapping,
        {
            "ldap_to_mo": {"EmailEmployee": {"_terminate_": "whatever", "uuid": ""}},
        },
    )
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(ConversionMapping, new_mapping)
    assert "UUID must not be empty if _terminate_ is set" in str(exc_info.value)


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
def test_discriminator_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert settings.discriminator_fields == []
    assert settings.discriminator_values == []

    exc_info: pytest.ExceptionInfo

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELDS", '["xBrugertype"]')
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "DISCRIMINATOR_VALUES must be set" in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELDS", '["xBrugertype"]')
        mpc.setenv("DISCRIMINATOR_VALUES", "[]")
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "DISCRIMINATOR_VALUES must be set" in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELDS", '["xBrugertype"]')
        mpc.setenv("DISCRIMINATOR_VALUES", "__invalid__")
        with pytest.raises(SettingsError) as exc_info:
            Settings()
        assert 'error parsing env var "discriminator_values"' in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELDS", '["xBrugertype"]')
        mpc.setenv("DISCRIMINATOR_VALUES", '["hello"]')
        settings = Settings()
        assert settings.discriminator_fields == ["xBrugertype"]
        assert settings.discriminator_values == ["hello"]


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
def test_dialect_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert settings.ldap_dialect == "AD"
    assert settings.ldap_unique_id_field == "objectGUID"

    exc_info: pytest.ExceptionInfo

    with monkeypatch.context() as mpc:
        mpc.setenv("LDAP_DIALECT", "UNKNOWN")
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "unexpected value; permitted: 'Standard', 'AD'" in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("LDAP_DIALECT", "Standard")
        settings = Settings()
        assert settings.ldap_dialect == "Standard"
        assert settings.ldap_unique_id_field == "entryUUID"

    with monkeypatch.context() as mpc:
        mpc.setenv("LDAP_DIALECT", "AD")
        settings = Settings()
        assert settings.ldap_dialect == "AD"
        assert settings.ldap_unique_id_field == "objectGUID"

    with monkeypatch.context() as mpc:
        mpc.setenv("LDAP_DIALECT", "Standard")
        mpc.setenv("ldap_unique_id_field", "myCustomField")
        settings = Settings()
        assert settings.ldap_dialect == "Standard"
        assert settings.ldap_unique_id_field == "myCustomField"

    with monkeypatch.context() as mpc:
        mpc.setenv("LDAP_DIALECT", "AD")
        mpc.setenv("ldap_unique_id_field", "myCustomField")
        settings = Settings()
        assert settings.ldap_dialect == "AD"
        assert settings.ldap_unique_id_field == "myCustomField"


@pytest.mark.parametrize(
    "object_class",
    (
        "Address",
        "Engagement",
        "ITUser",
        "Employee",
    ),
)
async def test_check_for_validity(object_class: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(
            LDAP2MOMapping,
            {
                "objectClass": object_class,
                "validity": "{{ dict(from_date=now()|mo_datestring) }}",
            },
        )

    assert "'validity' cannot be set on the ldap_to_mo mapping" in str(exc_info.value)


@pytest.mark.parametrize(
    "object_class",
    (
        "Address",
        "Engagement",
        "ITUser",
        "Employee",
    ),
)
async def test_check_for_superfluous_attributes(object_class: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(
            LDAP2MOMapping,
            {"objectClass": object_class, "non_existing_attribute": "failure"},
        )

    assert "Attributes {'non_existing_attribute'} are not allowed" in str(
        exc_info.value
    )


async def test_check_for_engagement_primary_specialcase():
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(
            LDAP2MOMapping,
            {
                "objectClass": "Engagement",
                "org_unit": "val",
                "job_function": "val",
                "user_key": "val",
                "engagement_type": "val",
                "person": "val",
            },
        )

    assert "Missing {'primary'} which are mandatory." in str(exc_info.value)


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.parametrize(
    "overrides, expected",
    (
        ({}, "'LDAP_CPR_ATTRIBUTE' and 'LDAP_IT_SYSTEM' cannot both be 'None'"),
        ({"LDAP_CPR_ATTRIBUTE": "EmployeeID"}, None),
        ({"LDAP_IT_SYSTEM": "ADUUID"}, None),
        ({"LDAP_CPR_ATTRIBUTE": "EmployeeID", "LDAP_IT_SYSTEM": "ADUUID"}, None),
    ),
)
async def test_correlation_configuration(
    monkeypatch: pytest.MonkeyPatch,
    overrides: dict[str, Any],
    expected: str | None,
) -> None:
    monkeypatch.delenv("LDAP_CPR_ATTRIBUTE", raising=False)
    monkeypatch.delenv("LDAP_IT_SYSTEM", raising=False)

    for key, value in overrides.items():
        monkeypatch.setenv(key, value)

    if expected is None:
        Settings()
    else:
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert expected in str(exc_info.value)


valid_jinja = [
    "",
    "hardcoded",
    "{{ foo == 42 }}",
    "{# comment #}",
    "{% if foo %} {{ foo == 42 }} {% else %} hardcoded {% endif %}",
    "{% set foo=42 %} {{ foo == 42 }}",
    "{{ func().__code__ }}",
    "{{ x.__class__.__init__.__globals__['Settings']().ldap_password }}",
]

invalid_jinja = [
    # Missing % in if
    "{% if } hardcoded {% endif %}",
    # Missing condition in if
    "{% if %} {{ foo == 42 }} {% endif %}",
    # Missing endif
    "{% if foo %} {{ foo == 42 }}",
    # Invalid markers for comment
    "{% comment %}",
]


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.parametrize("jinja_template", valid_jinja)
@pytest.mark.parametrize(
    "environment_variable", ["CONVERSION_MAPPING__MO2LDAP", "DISCRIMINATOR_FILTER"]
)
async def test_jinja_validator_valid(
    monkeypatch: pytest.MonkeyPatch, jinja_template: str, environment_variable: str
) -> None:
    monkeypatch.setenv("CONVERSION_MAPPING__MO2LDAP", jinja_template)
    Settings()


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.parametrize("jinja_template", invalid_jinja)
@pytest.mark.parametrize(
    "environment_variable, error_field",
    [
        ("CONVERSION_MAPPING__MO2LDAP", "mo2ldap"),
        ("DISCRIMINATOR_FILTER", "discriminator_filter"),
    ],
)
async def test_jinja_validator_invalid(
    monkeypatch: pytest.MonkeyPatch,
    jinja_template: str,
    environment_variable: str,
    error_field: str,
) -> None:
    monkeypatch.setenv(environment_variable, jinja_template)
    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "1 validation error for Settings" in str(exc_info.value)
    assert f"{error_field}\n  Unable to parse jinja" in str(exc_info.value)


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.parametrize("jinja_template", valid_jinja)
async def test_discriminator_values_jinja_validator_valid(
    monkeypatch: pytest.MonkeyPatch, jinja_template: str
) -> None:
    monkeypatch.setenv("DISCRIMINATOR_VALUES", json.dumps([jinja_template]))
    Settings()


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.parametrize("jinja_template", invalid_jinja)
async def test_discriminator_values_jinja_validator_invalid(
    monkeypatch: pytest.MonkeyPatch, jinja_template: str
) -> None:
    monkeypatch.setenv("DISCRIMINATOR_VALUES", json.dumps([jinja_template]))
    with pytest.raises(ValidationError) as exc_info:
        Settings()
    assert "1 validation error for Settings" in str(exc_info.value)
    assert "discriminator_values -> 0\n  Unable to parse jinja" in str(exc_info.value)


@pytest.mark.parametrize(
    "object_class",
    (
        "Address",
        "Engagement",
        "ITUser",
    ),
)
async def test_edit_only_validator(object_class: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(
            LDAP2MOMapping,
            {
                "_import_to_mo_": "edit_only",
                "_ldap_attributes_": [],
                "objectClass": object_class,
                "uuid": "",
            },
        )

    assert "Edit only is only supported for employees" in str(exc_info.value)


async def test_edit_only_validator_employee_ok() -> None:
    result = parse_obj_as(
        LDAP2MOMapping,
        {
            "_import_to_mo_": "edit_only",
            "_ldap_attributes_": [],
            "objectClass": "Employee",
            "uuid": "",
        },
    )
    assert result.import_to_mo == "edit_only"


@pytest.mark.parametrize("field", ["dn", "value"])
@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_disallowed_discriminator_fields(
    monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    monkeypatch.setenv("DISCRIMINATOR_VALUES", '["test"]')
    monkeypatch.setenv("DISCRIMINATOR_FIELDS", f'["{field}"]')

    with pytest.raises(ValueError) as exc_info:
        Settings()
    assert f"Invalid field in DISCRIMINATOR_FIELD(S): '{field}'" in str(exc_info.value)


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_allow_atmost_one_dc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "LDAP_CONTROLLERS",
        '[{"host": "host1.example.com"}, {"host": "host2.example.com"}]',
    )

    with pytest.raises(ValueError) as exc_info:
        Settings()
    errors = [
        "1 validation error for Settings\nldap_controllers",
        "At most one domain controller can be configured",
    ]
    for error in errors:
        assert error in str(exc_info.value)


minimal_valid_yaml_settings = """
# LDAP
ldap_controllers:
    - host: 21dc100.holstebro.dk
      use_ssl: 'true'
ldap_domain: holstebro.dk
ldap_cpr_attribute: employeeNumber
ldap_object_class: user
ldap_password: Only4service
ldap_search_base: OU=HK,DC=holstebro,DC=dk
ldap_user: svc_os2mo
# Mapping
conversion_mapping: {}
# LDAP AMQP
ldap_amqp:
    url: "amqp://msg_broker:5672/"
fastramqpi:
    # OS2mo
    client_id: ldap_import_export
    client_secret: "00000000-0000-0000-0000-000000000000"
    # AMQP
    amqp:
        url: "amqp://msg_broker:5672/"
    # Database
    database:
        host: "db"
        name: "ldap"
        user: "ldap"
        password: database-password-here
"""


async def test_load_yaml() -> None:
    def my_read(*args: Any, **kwargs: Any) -> str:
        return minimal_valid_yaml_settings

    with patch.object(pathlib.Path, "read_text", my_read):
        settings = Settings()
        assert one(settings.ldap_controllers).use_ssl is True
        assert settings.fastramqpi.database is not None
        assert settings.fastramqpi.database.host == "db"


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.envvar({"DISCRIMINATOR_VALUES": '["True"]'})
def test_discriminator_filter_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert settings.discriminator_fields == []
    assert settings.discriminator_filter is None

    exc_info: pytest.ExceptionInfo

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FILTER", "True")
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "DISCRIMINATOR_FIELD(s) must be set" in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FILTER", "True")
        mpc.setenv("DISCRIMINATOR_FIELDS", '["xBrugertype"]')
        settings = Settings()
        assert settings.discriminator_fields == ["xBrugertype"]
        assert settings.discriminator_filter == "True"

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FILTER", "True")
        mpc.setenv("DISCRIMINATOR_FIELDS", '["xBrugertype", "LDAP_SYNC"]')
        settings = Settings()
        assert settings.discriminator_fields == ["xBrugertype", "LDAP_SYNC"]
        assert settings.discriminator_filter == "True"


def test_jinja_template_repr() -> None:
    assert repr(JinjaTemplate("hello")) == "JinjaTemplate('hello')"


def test_jinja_template_non_string() -> None:
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(JinjaTemplate, 2)
    assert "__root__\n  string required" in str(exc_info.value)


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
def test_mo_to_ldap_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert settings.conversion_mapping.mo_to_ldap == []

    monkeypatch.setenv(
        "CONVERSION_MAPPING",
        json.dumps(
            {
                "mo_to_ldap": [
                    {
                        "identifier": "itsystem2group",
                        "routing_key": "itsystem",
                        "object_class": "groupOfNames",
                        "template": "{# this is a jinja comment #}",
                    }
                ]
            }
        ),
    )
    settings = Settings()
    configuration = one(settings.conversion_mapping.mo_to_ldap)
    assert configuration.identifier == "itsystem2group"
    assert configuration.routing_key == "itsystem"
    assert configuration.object_class == "groupOfNames"
    assert configuration.template == "{# this is a jinja comment #}"


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
def test_mo_to_ldap_mapping_multiple(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert settings.conversion_mapping.mo_to_ldap == []

    monkeypatch.setenv(
        "CONVERSION_MAPPING",
        json.dumps(
            {
                "mo_to_ldap": [
                    {
                        "identifier": "itsystem2group",
                        "routing_key": "itsystem",
                        "object_class": "groupOfNames",
                        "template": "{# this is a jinja comment #}",
                    },
                    {
                        "identifier": "person",
                        "routing_key": "person",
                        "object_class": "inetOrgPerson",
                        "template": "{% set nice=20 %}",
                    },
                ]
            }
        ),
    )
    settings = Settings()
    configuration1, configuration2 = settings.conversion_mapping.mo_to_ldap

    assert configuration1.identifier == "itsystem2group"
    assert configuration1.routing_key == "itsystem"
    assert configuration1.object_class == "groupOfNames"
    assert configuration1.template == "{# this is a jinja comment #}"

    assert configuration2.identifier == "person"
    assert configuration2.routing_key == "person"
    assert configuration2.object_class == "inetOrgPerson"
    assert configuration2.template == "{% set nice=20 %}"


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
def test_mo_to_ldap_mapping_invalid_routing_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings()
    assert settings.conversion_mapping.mo_to_ldap == []

    monkeypatch.setenv(
        "CONVERSION_MAPPING",
        json.dumps(
            {
                "mo_to_ldap": [
                    {
                        "identifier": "itsystem2group",
                        "routing_key": "this_is_an_invalid_routing_key",
                        "object_class": "groupOfNames",
                        "template": "{# this is a jinja comment #}",
                    }
                ]
            }
        ),
    )
    expected_error_snippets = [
        "conversion_mapping -> mo_to_ldap -> 0 -> routing_key",
        "unexpected value; permitted: 'address', 'association'",
        "unexpected value; permitted: 'employee.address.create'",
    ]
    with pytest.raises(ValidationError) as exc_info:
        Settings()
    for error_snippet in expected_error_snippets:
        assert error_snippet in str(exc_info.value)


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
def test_mo_to_ldap_mapping_invalid_template(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert settings.conversion_mapping.mo_to_ldap == []

    monkeypatch.setenv(
        "CONVERSION_MAPPING",
        json.dumps(
            {
                "mo_to_ldap": [
                    {
                        "identifier": "itsystem2group",
                        "routing_key": "itsystem",
                        "object_class": "groupOfNames",
                        "template": "{# this is a broken jinja comment }}",
                    }
                ]
            }
        ),
    )
    expected_error_snippets = [
        "conversion_mapping -> mo_to_ldap -> 0 -> template",
        "Unable to parse jinja (type=value_error)",
    ]
    with pytest.raises(ValidationError) as exc_info:
        Settings()
    for error_snippet in expected_error_snippets:
        assert error_snippet in str(exc_info.value)

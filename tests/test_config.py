# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from functools import partial
from typing import Any
from typing import cast

import pytest
from mergedeep import Strategy  # type: ignore
from mergedeep import merge  # type: ignore
from pydantic import ValidationError
from pydantic import parse_obj_as
from pydantic.env_settings import SettingsError
from structlog.testing import capture_logs

from mo_ldap_import_export.config import ConversionMapping
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
            "ldap_to_mo": {"EmailEmployee": {"_terminate_": "whatever"}},
        },
    )
    parse_obj_as(ConversionMapping, new_mapping)


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
def test_discriminator_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = Settings()
    assert settings.discriminator_field is None
    assert settings.discriminator_values == []

    exc_info: pytest.ExceptionInfo

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELD", "xBrugertype")
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "DISCRIMINATOR_VALUES must be set" in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELD", "xBrugertype")
        mpc.setenv("DISCRIMINATOR_FUNCTION", "__invalid__")
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "unexpected value; permitted: 'template'" in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELD", "xBrugertype")
        mpc.setenv("DISCRIMINATOR_VALUES", "[]")
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "DISCRIMINATOR_VALUES must be set" in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELD", "xBrugertype")
        mpc.setenv("DISCRIMINATOR_VALUES", "__invalid__")
        with pytest.raises(SettingsError) as exc_info:
            Settings()
        assert 'error parsing env var "discriminator_values"' in str(exc_info.value)

    with monkeypatch.context() as mpc:
        mpc.setenv("DISCRIMINATOR_FIELD", "xBrugertype")
        mpc.setenv("DISCRIMINATOR_VALUES", '["hello"]')
        settings = Settings()
        assert settings.discriminator_field == "xBrugertype"
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


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.parametrize(
    "jinja_template, invalid",
    (
        # Valid templates
        ("", False),
        ("hardcoded", False),
        ("{{ foo == 42 }}", False),
        ("{# comment #}", False),
        ("{% if foo %} {{ foo == 42 }} {% else %} hardcoded {% endif %}", False),
        ("{% set foo=42 %} {{ foo == 42 }}", False),
        ("{{ func().__code__ }}", False),
        ("{{ x.__class__.__init__.__globals__['Settings']().ldap_password }}", False),
        # Invalid templates'
        # Missing % in if
        ("{% if } hardcoded {% endif %}", True),
        # Missing condition in if
        ("{% if %} {{ foo == 42 }} {% endif %}", True),
        # Missing endif
        ("{% if foo %} {{ foo == 42 }}", True),
        # Invalid markers for comment
        ("{% comment %}", True),
    ),
)
async def test_mo2ldap_jinja_validator(
    monkeypatch: pytest.MonkeyPatch, jinja_template: str, invalid: bool
) -> None:
    monkeypatch.setenv("CONVERSION_MAPPING__MO2LDAP", jinja_template)

    if not invalid:
        Settings()
    else:
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "Unable to parse mo2ldap template" in str(exc_info.value)


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


@pytest.mark.parametrize(
    "field,fields",
    [
        (None, []),
        (None, ["sn"]),
        (None, ["sn", "cn"]),
        ("sn", []),
        ("sn", ["sn"]),
        ("sn", ["cn"]),
        ("sn", ["sn", "cn"]),
    ],
)
@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_combine_discriminator_fields(
    monkeypatch: pytest.MonkeyPatch,
    field: str | None,
    fields: list[str],
) -> None:
    monkeypatch.setenv("DISCRIMINATOR_VALUES", '["test"]')
    if field:
        monkeypatch.setenv("DISCRIMINATOR_FIELD", field)
    if fields:
        monkeypatch.setenv("DISCRIMINATOR_FIELDS", json.dumps(fields))

    settings = Settings()
    assert settings.discriminator_field == field

    if field:
        assert settings.discriminator_fields == fields + [field]
    else:
        assert settings.discriminator_fields == fields


@pytest.mark.parametrize("field", ["dn", "value"])
@pytest.mark.usefixtures("minimal_valid_environmental_variables")
async def test_disallowed_discriminator_fields(
    monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    monkeypatch.setenv("DISCRIMINATOR_VALUES", '["test"]')
    monkeypatch.setenv("DISCRIMINATOR_FIELD", field)

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


@pytest.mark.usefixtures("minimal_valid_environmental_variables")
@pytest.mark.envvar({"DISCRIMINATOR_FUNCTION": "template"})
async def test_discriminator_function_warning() -> None:
    with capture_logs() as cap_logs:
        Settings()
    assert cap_logs == [
        {
            "event": "Avoid setting 'discriminator_function' as it is scheduled for removal",
            "log_level": "warning",
        }
    ]

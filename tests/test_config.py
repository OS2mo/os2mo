# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from functools import partial

import pytest
from mergedeep import merge  # type: ignore
from mergedeep import Strategy
from pydantic import parse_obj_as
from pydantic import ValidationError

from mo_ldap_import_export.config import ConversionMapping


overlay = partial(merge, strategy=Strategy.TYPESAFE_ADDITIVE)


@pytest.fixture
def minimal_mapping() -> dict:
    return {
        "ldap_to_mo": {
            "Employee": {
                "objectClass": "ramodels.mo.employee.Employee",
                "_import_to_mo_": "false",
                "uuid": "{{ employee_uuid or NONE }}",
            }
        },
        "mo_to_ldap": {
            "Employee": {
                "objectClass": "inetOrgPerson",
                "_export_to_ldap_": "false",
            }
        },
        "username_generator": {"objectClass": "UserNameGenerator"},
    }


def test_minimal_config(minimal_mapping: dict) -> None:
    """Happy path test for the minimal acceptable mapping."""
    conversion_mapping = parse_obj_as(ConversionMapping, minimal_mapping)
    assert conversion_mapping.dict(exclude_unset=True, by_alias=True) == minimal_mapping


def test_unused_init_facets(minimal_mapping: dict) -> None:
    """Test that unutilized elements in init are disallowed."""
    new_mapping = overlay(
        minimal_mapping,
        {
            "init": {
                "facets": {
                    "employee_address_type": {
                        "EmailEmployee": {"title": "Mail (AD)", "scope": "EMAIL"}
                    }
                }
            }
        },
    )
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(ConversionMapping, new_mapping)
    assert "Unutilized elements in init configuration" in str(exc_info.value)


def test_unused_init_itsystems(minimal_mapping: dict) -> None:
    """Test that unutilized elements in init are disallowed."""
    new_mapping = overlay(
        minimal_mapping, {"init": {"it_systems": {"ADUUID": "Active Directory UUID"}}}
    )
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(ConversionMapping, new_mapping)
    assert "Unutilized elements in init configuration" in str(exc_info.value)


def test_address_type_employee_validator(minimal_mapping: dict) -> None:
    """Test that address_type template usage is checked."""
    new_mapping = overlay(
        minimal_mapping,
        {
            "init": {
                "facets": {
                    "employee_address_type": {
                        "EmailEmployee": {"title": "Mail (AD)", "scope": "EMAIL"}
                    }
                }
            },
            "ldap_to_mo": {
                "EmailEmployee": {
                    "objectClass": "ramodels.mo.details.address.Address",
                    "_import_to_mo_": "true",
                    "value": "{{ldap.mail or NONE}}",
                    "validity": "{{ dict(from_date = now()|mo_datestring) }}",
                    "address_type": "{{ dict(uuid=get_employee_address_type_uuid('EmailEmployee')) }}",
                    "person": "{{ dict(uuid=employee_uuid or NONE) }}",
                }
            },
            "mo_to_ldap": {
                "EmailEmployee": {
                    "objectClass": "user",
                    "_export_to_ldap_": "true",
                    "mail": "{{mo_employee_address.value}}",
                    "employeeID": "{{mo_employee.cpr_no}}",
                }
            },
        },
    )
    parse_obj_as(ConversionMapping, new_mapping)

    # Ruin address type reference
    new_mapping = overlay(
        new_mapping, {"ldap_to_mo": {"EmailEmployee": {"address_type": "fixed value"}}}
    )
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(ConversionMapping, new_mapping)
    assert "Address not templating address type UUID" in str(exc_info.value)


def test_address_type_org_unit_validator(minimal_mapping: dict) -> None:
    """Test that address_type template usage is checked."""
    new_mapping = overlay(
        minimal_mapping,
        {
            "init": {
                "facets": {
                    "org_unit_address_type": {
                        "EmailOrgUnit": {"title": "Mail (AD)", "scope": "EMAIL"}
                    }
                }
            },
            "ldap_to_mo": {
                "EmailOrgUnit": {
                    "objectClass": "ramodels.mo.details.address.Address",
                    "_import_to_mo_": "true",
                    "value": "{{ldap.mail or NONE}}",
                    "validity": "{{ dict(from_date = now()|mo_datestring) }}",
                    "address_type": "{{ dict(uuid=get_org_unit_address_type_uuid('EmailOrgUnit')) }}",
                    "org_unit": "{{ dict(uuid=get_or_create_org_unit_uuid(org_unit_path_string_from_dn(ldap.dn, 2))) }}",
                }
            },
            "mo_to_ldap": {
                "EmailOrgUnit": {
                    "objectClass": "user",
                    "_export_to_ldap_": "true",
                    "mail": "{{mo_org_unit_address.value}}",
                    "dn": "{{make_dn_from_org_unit_path(dn, nonejoin_orgs("
                    "OS2MO"
                    ", "
                    "demo"
                    ", get_org_unit_path_string(mo_org_unit_address.org_unit.uuid)))}}",
                }
            },
        },
    )
    parse_obj_as(ConversionMapping, new_mapping)

    # Ruin address type reference
    new_mapping = overlay(
        new_mapping, {"ldap_to_mo": {"EmailOrgUnit": {"address_type": "fixed value"}}}
    )
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(ConversionMapping, new_mapping)
    assert "Address not templating address type UUID" in str(exc_info.value)


def test_itsystem_validator(minimal_mapping: dict) -> None:
    """Test that itsystem template usage is checked."""
    new_mapping = overlay(
        minimal_mapping,
        {
            "init": {"it_systems": {"ADUUID": "Active Directory UUID"}},
            "ldap_to_mo": {
                "ADUUID": {
                    "objectClass": "ramodels.mo.details.it_system.ITUser",
                    "_import_to_mo_": "true",
                    "user_key": "{{ ldap.objectGUID|remove_curly_brackets }}",
                    "itsystem": "{{ dict(uuid=get_it_system_uuid('ADUUID')) }}",
                    "validity": "{{ dict(from_date=now()|mo_datestring) }}",
                    "person": "{{ dict(uuid=employee_uuid or NONE) }}",
                }
            },
            "mo_to_ldap": {
                "ADUUID": {
                    "objectClass": "user",
                    "_export_to_ldap_": "true",
                    "objectGUID": "{{ "
                    "{"
                    " + mo_employee_it_user.user_key + "
                    "}"
                    " }}",
                    "employeeID": "{{mo_employee.cpr_no}}",
                }
            },
        },
    )
    parse_obj_as(ConversionMapping, new_mapping)

    # Ruin itsystem reference
    new_mapping = overlay(
        new_mapping, {"ldap_to_mo": {"ADUUID": {"itsystem": "fixed value"}}}
    )
    with pytest.raises(ValidationError) as exc_info:
        parse_obj_as(ConversionMapping, new_mapping)
    assert "IT-System not templating it-system UUID" in str(exc_info.value)

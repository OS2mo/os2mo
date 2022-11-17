# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from typing import Any
from typing import Dict

import structlog
from fastramqpi.context import Context
from jinja2 import Environment
from jinja2 import Undefined
from ldap3.utils.ciDict import CaseInsensitiveDict
from ramodels.mo.employee import Employee

from .exceptions import CprNoNotFound
from .exceptions import IncorrectMapping
from .ldap_classes import LdapEmployee


def read_mapping_json(filename: str) -> Any:
    with open(filename, "r") as file:
        data = "\n".join(file.readlines())
        data = re.sub("//[^\n]*", "", data)
        return json.loads(data)


def find_cpr_field(mapping):
    """
    Get the field which contains the CPR number in LDAP
    """
    logger = structlog.get_logger()
    try:
        mo_to_ldap = mapping["mo_to_ldap"]
    except KeyError:
        raise IncorrectMapping("Missing mapping 'mo_to_ldap'")
    try:
        user_attrs_mapping = mo_to_ldap["user_attrs"]
    except KeyError:
        raise IncorrectMapping("Missing 'user_attrs' in mapping 'mo_to_ldap'")

    # See if we can find a match for this search field/result
    search_result = "123"
    search_field = "cpr_no"

    mo_dict = {search_field: search_result}
    cpr_field = None
    for ldap_field_name, template in user_attrs_mapping.items():
        value = template.render({"mo": mo_dict}).strip()

        if value == search_result:
            cpr_field = ldap_field_name
            logger.info("Found CPR field in LDAP: '%s'" % cpr_field)
            break

    if cpr_field is None:
        raise CprNoNotFound("CPR field not found")

    return cpr_field


logger = structlog.get_logger()


class EmployeeConverter:
    def __init__(self, context: Context):

        self.user_context = context["user_context"]
        self.settings = self.user_context["settings"]
        mapping = self.user_context["mapping"]

        environment = Environment(undefined=Undefined)
        environment.filters["splitlast"] = EmployeeConverter.filter_splitlast
        environment.filters["splitfirst"] = EmployeeConverter.filter_splitfirst
        self.mapping = self._populate_mapping_with_templates(
            mapping,
            environment,
        )

        self.cpr_field = find_cpr_field(mapping)

    @staticmethod
    def filter_splitfirst(text):
        """
        Splits a string at the first space, returning two elements
        This is convenient for splitting a name into a givenName and a surname
        and works for names with no spaces (surname will then be empty)
        """
        if text is not None:
            text = str(text)
            if text != "":
                s = text.split(" ", 1)
                return s if len(s) > 1 else (s + [""])
        return ["", ""]

    @staticmethod
    def filter_splitlast(text):
        """
        Splits a string at the last space, returning two elements
        This is convenient for splitting a name into a givenName and a surname
        and works for names with no spaces (givenname will then be empty)
        """
        if text is not None:
            text = str(text)
            if text != "":
                text = str(text)
                s = text.split(" ")
                return [" ".join(s[:-1]), s[-1]]
        return ["", ""]

    def _populate_mapping_with_templates(
        self, mapping: Dict[str, Any], environment: Environment
    ):
        for key, value in mapping.items():
            if type(value) == str:
                mapping[key] = environment.from_string(value)
            elif type(value) == dict:
                mapping[key] = self._populate_mapping_with_templates(value, environment)
        return mapping

    def to_ldap(self, mo_object: Employee) -> LdapEmployee:
        ldap_object = {}
        try:
            mapping = self.mapping["mo_to_ldap"]
        except KeyError:
            raise IncorrectMapping("Missing mapping 'mo_to_ldap'")
        try:
            user_attrs_mapping = mapping["user_attrs"]
        except KeyError:
            raise IncorrectMapping("Missing 'user_attrs' in mapping 'mo_to_ldap'")
        for ldap_field_name, template in user_attrs_mapping.items():
            ldap_object[ldap_field_name] = template.render({"mo": mo_object})

        #  Common Name
        cn = "CN=%s %s - %s" % (
            mo_object.givenname,
            mo_object.surname,
            mo_object.cpr_no or "",
        )

        ou = "OU=Users,%s" % self.settings.ldap_organizational_unit  # Org. Unit
        dc = self.settings.ldap_search_base  # Domain Component
        dn = ",".join([cn, ou, dc])  # Distinguished Name
        ldap_object["dn"] = dn
        ldap_object["cpr"] = ldap_object[self.cpr_field]

        return LdapEmployee(**ldap_object)

    def from_ldap(self, ldap_object: LdapEmployee) -> Employee:
        ldap_dict = CaseInsensitiveDict(
            {
                key: value[0] if type(value) == list and len(value) == 1 else value
                for key, value in ldap_object.dict().items()
            }
        )
        mo_dict = {}
        try:
            mapping = self.mapping["ldap_to_mo"]
        except KeyError:
            raise IncorrectMapping("Missing mapping 'ldap_to_mo'")
        try:
            user_attrs_mapping = mapping["user_attrs"]
        except KeyError:
            raise IncorrectMapping("Missing 'user_attrs' in mapping 'ldap_to_mo'")
        for mo_field_name, template in user_attrs_mapping.items():
            value = template.render({"ldap": ldap_dict}).strip()
            if value != "None":
                mo_dict[mo_field_name] = value

        logger.info(mo_dict)
        return Employee(**mo_dict)

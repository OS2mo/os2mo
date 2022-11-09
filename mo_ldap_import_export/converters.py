# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from typing import Any
from typing import Dict

from jinja2 import Environment
from jinja2 import Undefined
from ldap3.utils.ciDict import CaseInsensitiveDict
from ramodels.mo.employee import Employee

from .dataloaders import LdapEmployee


def read_mapping_json(filename: str) -> Any:
    with open(filename, "r") as file:
        data = "\n".join(file.readlines())
        data = re.sub("//[^\n]*", "", data)
        return json.loads(data)


class EmployeeConverter:
    def __init__(self, mapping: Dict[str, Any] | str):
        environment = Environment(undefined=Undefined)
        environment.filters["splitlast"] = EmployeeConverter.filter_splitlast
        environment.filters["splitfirst"] = EmployeeConverter.filter_splitfirst
        self.mapping = self._populate_mapping_with_templates(
            read_mapping_json(mapping) if type(mapping) is str else mapping,
            environment,
        )

    @staticmethod
    def filter_splitfirst(text):
        """
        Splits a string at the first space, returning two elements
        This is convenient for splitting a name into a givenName and a surname
        and works for names with no spaces (surname will then be empty)
        """
        s = text.split(" ", 1)
        return s if len(s) > 1 else (s + [""])

    @staticmethod
    def filter_splitlast(text):
        """
        Splits a string at the last space, returning two elements
        This is convenient for splitting a name into a givenName and a surname
        and works for names with no spaces (givenname will then be empty)
        """
        s = text.split(" ")
        return [" ".join(s[:-1]), s[-1]]

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
        mapping = self.mapping["mo_to_ldap"]
        if "user_attrs" in mapping:
            user_attrs_mapping = mapping["user_attrs"]
            for ldap_field_name, template in user_attrs_mapping.items():
                ldap_object[ldap_field_name] = template.render({"mo": mo_object})
        return LdapEmployee(**ldap_object)

    def from_ldap(self, ldap_object: LdapEmployee) -> Employee:
        ldap_dict = CaseInsensitiveDict(
            {
                key: value[0] if type(value) == list and len(value) == 1 else value
                for key, value in ldap_object.dict().items()
            }
        )
        mo_dict = {"uuid": ldap_dict["objectGUID"]}
        mapping = self.mapping["ldap_to_mo"]
        if "user_attrs" in mapping:
            user_attrs_mapping = mapping["user_attrs"]
            for mo_field_name, template in user_attrs_mapping.items():
                value = template.render({"ldap": ldap_dict}).strip()
                if value != "None":
                    mo_dict[mo_field_name] = value
        return Employee(**mo_dict)

# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Ldap class definitions"""
from pydantic import BaseModel
from pydantic import Extra


class LdapObject(BaseModel, extra=Extra.allow):
    dn: str  # LDAP requires that the class contains a 'dn' (Distinguished Name) field

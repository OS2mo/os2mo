# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""Ldap class definitions"""
from pydantic import BaseModel
from pydantic import Extra


class LdapEmployee(BaseModel, extra=Extra.allow):
    dn: str  # LDAP requires that the class contains a 'dn' (Distinguished Name) field
    cpr: str  # We require that the class contains a cpr field.
    # Apart from that, LDAP decides the fields in this model.

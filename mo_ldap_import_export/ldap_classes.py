# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Ldap class definitions"""

from pydantic import BaseModel
from pydantic import Extra


class LdapObject(BaseModel, extra=Extra.allow):  # type: ignore
    dn: str  # LDAP requires that the class contains a 'dn' (Distinguished Name) field

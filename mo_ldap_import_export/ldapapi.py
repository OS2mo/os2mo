# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import structlog
from ldap3 import BASE
from ldap3 import Connection
from ldap3.utils.dn import safe_dn

from .config import Settings
from .ldap import single_object_search
from .types import DN
from .utils import extract_ou_from_dn

logger = structlog.stdlib.get_logger()


class LDAPAPI:
    def __init__(self, settings: Settings, ldap_connection: Connection) -> None:
        self.settings = settings
        self.ldap_connection = ldap_connection

    # TODO: Move this to settings?
    def ou_in_ous_to_write_to(self, dn: str) -> bool:
        """
        Determine if an OU is among those to which we are allowed to write.
        """
        if "" in self.settings.ldap_ous_to_write_to:
            # Empty string means that it is allowed to write to all OUs
            return True

        ou = extract_ou_from_dn(dn)
        ous_to_write_to = [safe_dn(ou) for ou in self.settings.ldap_ous_to_write_to]
        for ou_to_write_to in ous_to_write_to:
            if ou.endswith(ou_to_write_to):
                # If an OU ends with one of the OUs-to-write-to, it's OK.
                # For example, if we are only allowed to write to "OU=foo",
                # Then we are also allowed to write to "OU=bar,OU=foo", which is a
                # sub-OU inside "OU=foo"
                return True

        logger.info("OU not in OUs to write", ou=ou, ous_to_write_to=ous_to_write_to)
        return False

    async def get_ldap_dn(self, unique_ldap_uuid: UUID) -> DN:
        """
        Given an unique_ldap_uuid, find the DistinguishedName
        """
        logger.info("Looking for LDAP object", unique_ldap_uuid=unique_ldap_uuid)
        searchParameters = {
            "search_base": self.settings.ldap_search_base,
            "search_filter": f"(&(objectclass=*)({self.settings.ldap_unique_id_field}={unique_ldap_uuid}))",
            "attributes": [],
        }

        # Special-case for AD
        if self.settings.ldap_unique_id_field == "objectGUID":
            searchParameters = {
                "search_base": f"<GUID={unique_ldap_uuid}>",
                "search_filter": "(objectclass=*)",
                "attributes": [],
                "search_scope": BASE,
            }

        search_result = await single_object_search(
            searchParameters, self.ldap_connection
        )
        dn: str = search_result["dn"]
        return dn

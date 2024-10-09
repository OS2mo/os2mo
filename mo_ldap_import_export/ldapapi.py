# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
from functools import partialmethod
from typing import Literal
from uuid import UUID

import structlog
from ldap3 import BASE
from ldap3 import Connection
from ldap3.utils.dn import safe_dn
from more_itertools import only

from .config import Settings
from .exceptions import InvalidChangeDict
from .exceptions import ReadOnlyException
from .ldap import ldap_compare
from .ldap import ldap_modify
from .ldap import object_search
from .ldap import paged_search
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

    async def modify_ldap(
        self,
        operation: Literal["MODIFY_DELETE", "MODIFY_REPLACE"],
        dn: str,
        attribute: str,
        value: list[str] | str,
    ) -> dict | None:
        """
        Modifies LDAP
        """
        # TODO: Remove this when ldap3s read-only flag works
        if self.settings.ldap_read_only:
            logger.info(
                "LDAP connection is read-only",
                operation="modify_ldap",
                dn=dn,
                attribute=attribute,
            )
            raise ReadOnlyException("LDAP connection is read-only")

        # Checks
        if not self.ou_in_ous_to_write_to(dn):
            return None

        if isinstance(value, list):
            value = only(
                value,
                default="",
                too_long=InvalidChangeDict(
                    "Exactly one value can be changed at a time"
                ),
            )

        # Compare to LDAP
        value_exists = await ldap_compare(self.ldap_connection, dn, attribute, value)

        # If the value is already as expected, and we are not deleting, we are done
        if value_exists and "DELETE" not in operation:
            logger.info(
                "Attribute value already exists",
                attribute=attribute,
                value_to_modify=value,
            )
            return None

        # Modify LDAP
        changes = {attribute: [(operation, value)]}
        logger.info("Uploading the changes", changes=changes, dn=dn)
        _, result = await ldap_modify(self.ldap_connection, dn, changes)
        logger.info("LDAP Result", result=result, dn=dn)
        return result

    delete_ldap = partialmethod(modify_ldap, "MODIFY_DELETE")
    replace_ldap = partialmethod(modify_ldap, "MODIFY_REPLACE")

    async def load_ldap_OUs(self, search_base: str | None = None) -> dict:
        """
        Returns a dictionary where the keys are OU strings and the items are dicts
        which contain information about the OU
        """
        searchParameters: dict = {
            "search_filter": "(objectclass=OrganizationalUnit)",
            "attributes": [],
        }

        responses = await paged_search(
            self.settings,
            self.ldap_connection,
            searchParameters,
            search_base=search_base,
            mute=True,
        )
        dns = [r["dn"] for r in responses]

        user_object_class = self.settings.ldap_user_objectclass
        dn_responses = await asyncio.gather(
            *[
                object_search(
                    {
                        "search_base": dn,
                        "search_filter": f"(objectclass={user_object_class})",
                        "attributes": [],
                        "size_limit": 1,
                    },
                    self.ldap_connection,
                )
                for dn in dns
            ]
        )
        dn_map = dict(zip(dns, dn_responses, strict=False))

        return {
            extract_ou_from_dn(dn): {
                "empty": len(dn_map[dn]) == 0,
                "dn": dn,
            }
            for dn in dns
        }

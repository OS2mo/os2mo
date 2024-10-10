# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
from contextlib import suppress
from functools import partialmethod
from typing import Any
from typing import Literal
from typing import cast
from uuid import UUID

import structlog
from ldap3 import BASE
from ldap3 import Connection
from ldap3.utils.dn import safe_dn
from more_itertools import one
from more_itertools import only
from ramodels.mo._shared import validate_cpr

from .config import Settings
from .exceptions import InvalidChangeDict
from .exceptions import NoObjectsReturnedException
from .exceptions import ReadOnlyException
from .ldap import get_ldap_object
from .ldap import ldap_add
from .ldap import ldap_compare
from .ldap import ldap_modify
from .ldap import single_object_search
from .types import DN
from .types import CPRNumber
from .utils import extract_ou_from_dn
from .utils import is_exception

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
            logger.info(
                "Not allowed to write to the specified OU",
                operation="modify_ldap",
                dn=dn,
            )
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

    async def add_ldap_object(self, dn: str, attributes: dict[str, Any] | None = None):
        """
        Adds a new object to LDAP

        Parameters
        ---------------
        attributes : dict
            dictionary with attributes to populate in LDAP, when creating the user.
            See https://ldap3.readthedocs.io/en/latest/add.html for more information

        """
        # TODO: Remove this when ldap3s read-only flag works
        if self.settings.ldap_read_only:
            logger.info(
                "LDAP connection is read-only",
                operation="add_ldap_object",
                dn=dn,
                attributes=attributes,
            )
            raise ReadOnlyException("LDAP connection is read-only")

        if not self.settings.add_objects_to_ldap:
            logger.info(
                "Adding LDAP objects is disabled",
                operation="add_ldap_object",
                dn=dn,
                attributes=attributes,
            )
            raise ReadOnlyException("Adding LDAP objects is disabled")

        if not self.ou_in_ous_to_write_to(dn):
            logger.info(
                "Not allowed to write to the specified OU",
                operation="add_ldap_object",
                dn=dn,
                attributes=attributes,
            )
            raise ReadOnlyException("Not allowed to write to the specified OU")

        logger.info("Adding user to LDAP", dn=dn, attributes=attributes)
        employee_object_class = self.settings.conversion_mapping.mo_to_ldap[
            "Employee"
        ].objectClass
        _, result = await ldap_add(
            self.ldap_connection,
            dn,
            employee_object_class,
            attributes=attributes,
        )
        logger.info("LDAP Result", result=result, dn=dn)

    async def get_ldap_unique_ldap_uuid(self, dn: str) -> UUID:
        """
        Given a DN, find the unique_ldap_uuid
        """
        logger.info("Looking for LDAP object", dn=dn)
        ldap_object = await get_ldap_object(
            self.ldap_connection, dn, [self.settings.ldap_unique_id_field]
        )
        uuid = getattr(ldap_object, self.settings.ldap_unique_id_field)
        if not uuid:
            # Some computer-account objects has no samaccountname
            raise NoObjectsReturnedException(
                f"Object has no {self.settings.ldap_unique_id_field}"
            )
        return UUID(uuid)

    async def convert_ldap_uuids_to_dns(self, ldap_uuids: set[UUID]) -> set[DN]:
        # TODO: DataLoader / bulk here instead of this
        results = await asyncio.gather(
            *[self.get_ldap_dn(uuid) for uuid in ldap_uuids],
            return_exceptions=True,
        )
        exceptions = cast(list[Exception], list(filter(is_exception, results)))
        if exceptions:
            raise ExceptionGroup("Exceptions during UUID2DN translation", exceptions)
        return cast(set[DN], set(results))

    async def dn2cpr(self, dn: DN) -> CPRNumber | None:
        if self.settings.ldap_cpr_attribute is None:
            return None

        ldap_object = await get_ldap_object(
            self.ldap_connection, dn, [self.settings.ldap_cpr_attribute]
        )
        # Try to get the cpr number from LDAP and use that.
        with suppress(ValueError):
            raw_cpr_no = getattr(ldap_object, self.settings.ldap_cpr_attribute)
            # NOTE: Not sure if this only necessary for the mocked server or not
            if isinstance(raw_cpr_no, list):
                raw_cpr_no = one(raw_cpr_no)
            cpr_no = validate_cpr(str(raw_cpr_no))
            assert cpr_no is not None
            return CPRNumber(cpr_no)
        return None

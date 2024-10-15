# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
from contextlib import suppress
from typing import Any
from typing import cast
from uuid import UUID

import structlog
from ldap3 import BASE
from ldap3 import Connection
from ldap3.utils.dn import safe_dn
from more_itertools import one
from ramodels.mo._shared import validate_cpr

from .config import Settings
from .exceptions import NoObjectsReturnedException
from .exceptions import ReadOnlyException
from .ldap import get_ldap_object
from .ldap import ldap_add
from .ldap import make_ldap_object
from .ldap import object_search
from .ldap import single_object_search
from .ldap_classes import LdapObject
from .types import DN
from .types import CPRNumber
from .utils import combine_dn_strings
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
        # TODO: Clean this up when settings.ldap_object_class is required
        settings_default_ldap_class = self.settings.ldap_object_class
        old_default_ldap_class = self.settings.conversion_mapping.mo_to_ldap[
            "Employee"
        ].objectClass
        # One of these must be set
        assert (
            settings_default_ldap_class is not None
            or old_default_ldap_class is not None
        )
        employee_object_class: str = cast(
            str, settings_default_ldap_class or old_default_ldap_class
        )

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

    async def cpr2dns(self, cpr_no: CPRNumber) -> set[DN]:
        try:
            validate_cpr(cpr_no)
        except (ValueError, TypeError) as error:
            raise NoObjectsReturnedException(f"cpr_no '{cpr_no}' is invalid") from error

        if not self.settings.ldap_cpr_attribute:
            raise NoObjectsReturnedException("cpr_field is not configured")

        search_base = self.settings.ldap_search_base
        ous_to_search_in = self.settings.ldap_ous_to_search_in
        search_bases = [
            combine_dn_strings([ou, search_base]) for ou in ous_to_search_in
        ]

        # TODO: Clean this up when settings.ldap_object_class is required
        settings_default_ldap_class = self.settings.ldap_object_class
        old_default_ldap_class = self.settings.conversion_mapping.mo_to_ldap[
            "Employee"
        ].objectClass
        # One of these must be set
        assert (
            settings_default_ldap_class is not None
            or old_default_ldap_class is not None
        )
        object_class: str = cast(
            str, settings_default_ldap_class or old_default_ldap_class
        )

        object_class_filter = f"objectclass={object_class}"
        cpr_filter = f"{self.settings.ldap_cpr_attribute}={cpr_no}"

        searchParameters = {
            "search_base": search_bases,
            "search_filter": f"(&({object_class_filter})({cpr_filter}))",
            "attributes": [],
        }
        search_results = await object_search(searchParameters, self.ldap_connection)
        ldap_objects: list[LdapObject] = [
            await make_ldap_object(search_result, self.ldap_connection)
            for search_result in search_results
        ]
        dns = {obj.dn for obj in ldap_objects}
        logger.info("Found LDAP(s) object", dns=dns)
        return set(dns)

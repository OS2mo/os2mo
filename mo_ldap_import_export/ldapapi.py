# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from typing import Any
from typing import cast

import structlog
from ldap3 import BASE
from ldap3 import MODIFY_REPLACE
from ldap3 import Connection
from ldap3.core.exceptions import LDAPInvalidValueError
from ldap3.core.exceptions import LDAPNoSuchObjectResult
from ldap3.utils.dn import escape_rdn
from ldap3.utils.dn import parse_dn
from ldap3.utils.dn import safe_dn
from more_itertools import one
from more_itertools import only
from more_itertools import partition

from .config import Settings
from .exceptions import NoObjectsReturnedException
from .exceptions import ReadOnlyException
from .ldap import get_ldap_object
from .ldap import ldap_add
from .ldap import ldap_modify
from .ldap import ldap_modify_dn
from .ldap import make_ldap_object
from .ldap import object_search
from .ldap import single_object_search
from .ldap_classes import LdapObject
from .types import DN
from .types import LDAPUUID
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

    async def get_ldap_dn(self, unique_ldap_uuid: LDAPUUID) -> DN:
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

    async def add_ldap_object(self, dn: str, attributes: dict[str, Any]) -> None:
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

        # During edits empty lists are used to clear attributes, however they are not
        # allowed on creation since attributes are by default created as empty if no
        # value is explicitly provided. Thus we can safely filter empty values out.
        attributes = {key: value for key, value in attributes.items() if value != []}

        # Attributes which are part of the DN should not be set in `attributes` as well.
        # They will automatically be set by indirection via the DN.
        dn_attributes = {
            attribute.casefold() for attribute, value, seperator in parse_dn(dn)
        }
        attributes = {
            key: value
            for key, value in attributes.items()
            if key.casefold() not in dn_attributes
        }

        logger.info("Adding user to LDAP", dn=dn, attributes=attributes)
        employee_object_class = self.settings.ldap_object_class
        _, result = await ldap_add(
            self.ldap_connection,
            dn,
            employee_object_class,
            attributes=attributes,
        )
        logger.info("LDAP Result", result=result, dn=dn)

    async def get_ldap_unique_ldap_uuid(self, dn: str) -> LDAPUUID:
        """
        Given a DN, find the unique_ldap_uuid
        """
        logger.info("Looking for LDAP object", dn=dn)
        ldap_object = await get_ldap_object(
            self.ldap_connection, dn, {self.settings.ldap_unique_id_field}
        )
        uuid = getattr(ldap_object, self.settings.ldap_unique_id_field)
        if not uuid:
            # Some computer-account objects has no samaccountname
            raise NoObjectsReturnedException(
                f"Object has no {self.settings.ldap_unique_id_field}"
            )
        return LDAPUUID(uuid)

    async def convert_ldap_uuids_to_dns(self, ldap_uuids: set[LDAPUUID]) -> set[DN]:
        # TODO: DataLoader / bulk here instead of this
        results = await asyncio.gather(
            *[self.get_ldap_dn(uuid) for uuid in ldap_uuids],
            return_exceptions=True,
        )
        dns, exceptions = partition(is_exception, results)
        other_exceptions, not_found_exceptions = partition(
            lambda e: isinstance(e, NoObjectsReturnedException), exceptions
        )
        if not_found_exceptions_list := list(not_found_exceptions):
            logger.warning(
                "Unable to convert LDAP UUIDs to DNs",
                not_found=not_found_exceptions_list,
            )
        if other_exceptions_list := list(other_exceptions):
            raise ExceptionGroup(
                "Exceptions during UUID2DN translation",
                cast(list[Exception], other_exceptions_list),
            )
        return cast(set[DN], set(dns))

    async def dn2cpr(self, dn: DN) -> CPRNumber | None:
        if self.settings.ldap_cpr_attribute is None:
            return None

        ldap_object = await get_ldap_object(
            self.ldap_connection, dn, {self.settings.ldap_cpr_attribute}
        )
        # Try to get the cpr number from LDAP and use that.
        raw_cpr_number = getattr(ldap_object, self.settings.ldap_cpr_attribute)
        assert raw_cpr_number is not None
        # TODO: Figure out when this is a list
        if isinstance(raw_cpr_number, list):
            raw_cpr_number = only(raw_cpr_number)
        if raw_cpr_number is None:
            return None
        cpr_number = str(raw_cpr_number)
        return CPRNumber(cpr_number)

    async def cpr2dns(self, cpr_number: CPRNumber) -> set[DN]:
        if not self.settings.ldap_cpr_attribute:
            raise NoObjectsReturnedException("cpr_field is not configured")

        search_base = self.settings.ldap_search_base
        ous_to_search_in = self.settings.ldap_ous_to_search_in
        search_bases = [
            combine_dn_strings([ou, search_base]) for ou in ous_to_search_in
        ]

        object_class = self.settings.ldap_object_class
        object_class_filter = f"objectclass={object_class}"
        cpr_filter = f"{self.settings.ldap_cpr_attribute}={cpr_number}"

        searchParameters = {
            "search_base": search_bases,
            "search_filter": f"(&({object_class_filter})({cpr_filter}))",
            "attributes": [],
        }
        try:
            search_results = await object_search(searchParameters, self.ldap_connection)
        except LDAPNoSuchObjectResult:
            return set()
        ldap_objects: list[LdapObject] = [
            await make_ldap_object(search_result, self.ldap_connection)
            for search_result in search_results
        ]
        dns = {obj.dn for obj in ldap_objects}
        logger.info("Found LDAP(s) object", dns=dns)
        return set(dns)

    async def modify_ldap_object(
        self,
        dn: DN,
        requested_changes: dict[str, list],
    ) -> None:
        """
        Parameters
        -------------
        object_to_modify : LDAPObject
            object to upload to LDAP
        delete: bool
            Set to True to delete contents in LDAP, instead of creating/modifying them
        """
        # TODO: Remove this when ldap3s read-only flag works
        if self.settings.ldap_read_only:
            logger.info(
                "LDAP connection is read-only",
                operation="modify_ldap",
                dn=dn,
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

        if not requested_changes:
            logger.info("Not writing to LDAP as changeset is empty", dn=dn)
            return None

        logger.info("Uploading object", dn=dn, requested_changes=requested_changes)

        # The fields of the DN cannot be changed using LDAP's modify(), but
        # must instead be changed using modify_dn(). We normalise casing since
        # Microsoft AD is case-insensitive, so attributes written do not
        # necessarily match attributes read as part of the DN.
        modify_dn_attributes = {
            attribute.casefold() for attribute, value, seperator in parse_dn(dn)
        }

        # MODIFY-LDAP
        # Transform key-value changes to LDAP format
        modify_changes = {
            attribute: [(MODIFY_REPLACE, values)]
            for attribute, values in requested_changes.items()
            if attribute.casefold() not in modify_dn_attributes
        }
        # We do not attempt to call ldap_modify if there are no attribute changes,
        # otherwise it would produce an error and block us from making the DN changes
        # Thus to ensure we can change DN attributes alone, we must have this check.
        if modify_changes:
            try:
                # Modify LDAP
                logger.info("Uploading the changes", changes=requested_changes, dn=dn)
                _, result = await ldap_modify(self.ldap_connection, dn, modify_changes)
                logger.info("LDAP Result", result=result, dn=dn)
            except LDAPInvalidValueError as exc:
                logger.exception("LDAP modify failed", dn=dn, changes=requested_changes)
                raise exc

        # MODIFY-DN
        ldap_uuid = await self.get_ldap_unique_ldap_uuid(dn)
        requested_dn_changes = {
            attribute: values
            for attribute, values in requested_changes.items()
            if attribute.casefold() in modify_dn_attributes
        }
        for attribute, values in requested_dn_changes.items():
            # The user's DN is changed by our modifications, but its UUID does not
            current_dn = await self.get_ldap_dn(ldap_uuid)
            try:
                # Modify LDAP-DN
                logger.info(
                    "Changing object DN",
                    current_dn=current_dn,
                    attribute=attribute,
                    value=values,
                )
                rdn = f"{attribute}={escape_rdn(one(values))}"
                _, result = await ldap_modify_dn(self.ldap_connection, current_dn, rdn)
                logger.info("LDAP Result", result=result, current_dn=current_dn)
            except LDAPInvalidValueError as exc:  # pragma: no cover
                logger.exception(
                    "LDAP modify-dn failed",
                    current_dn=current_dn,
                    changes=requested_changes,
                )
                raise exc

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from contextlib import suppress
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
from ldap3.utils.dn import safe_rdn
from more_itertools import one
from more_itertools import only
from more_itertools import partition

from .config import Settings
from .exceptions import NoObjectsReturnedException
from .exceptions import ReadOnlyException
from .ldap import LDAPConnection
from .ldap import construct_assertion_control
from .ldap import construct_assertion_control_filter
from .ldap import get_ldap_object
from .ldap import make_ldap_object
from .ldap import object_search
from .ldap import single_object_search
from .ldap_classes import LdapObject
from .types import DN
from .types import LDAPUUID
from .types import CPRNumber
from .utils import combine_dn_strings
from .utils import ensure_list
from .utils import extract_ou_from_dn
from .utils import is_exception

logger = structlog.stdlib.get_logger()


class LDAPAPI:
    def __init__(self, settings: Settings, ldap_connection: Connection) -> None:
        self.settings = settings
        self.ldap_connection = LDAPConnection(ldap_connection)

    @property
    def connection(self) -> Connection:
        return self.ldap_connection.connection

    # TODO: Move this to settings?
    def ou_in_ous_to_write_to(self, dn: DN) -> bool:
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

    async def get_object_by_uuid(
        self, unique_ldap_uuid: LDAPUUID, attributes: set | None = None
    ) -> LdapObject | None:
        """Fetch an LDAP object by its UUID.

        Args:
            unique_ldap_uuid: The UUID of the LDAP object.
            attributes: The list of attributes to fetch.

        Returns:
            The fetched object if found or None if no object could be found.
        """
        if attributes is None:
            attributes = {"*"}

        logger.info("Looking for LDAP object", unique_ldap_uuid=unique_ldap_uuid)
        searchParameters = {
            "search_base": self.settings.ldap_search_base,
            "search_filter": f"(&(objectclass=*)({self.settings.ldap_unique_id_field}={unique_ldap_uuid}))",
            "attributes": attributes,
        }

        # Special-case for AD
        if self.settings.ldap_unique_id_field == "objectGUID":
            searchParameters = {
                "search_base": f"<GUID={unique_ldap_uuid}>",
                "search_filter": "(objectclass=*)",
                "attributes": attributes,
                "search_scope": BASE,
            }

        with suppress(NoObjectsReturnedException):
            search_result = await single_object_search(
                searchParameters, self.connection
            )
            return await make_ldap_object(
                search_result, self.ldap_connection.connection, nest=False
            )
        return None

    async def get_ldap_dn(self, unique_ldap_uuid: LDAPUUID) -> DN:
        """
        Given an unique_ldap_uuid, find the DistinguishedName
        """
        ldap_object = await self.get_object_by_uuid(unique_ldap_uuid)
        if ldap_object is None:
            raise NoObjectsReturnedException(
                f"Found no entries for uuid={unique_ldap_uuid}"
            )
        return ldap_object.dn

    async def ensure_ldap_object(
        self, dn: DN, attributes: dict[str, list], object_class: str, create: bool
    ) -> DN:
        """
        Ensures an object exists at `dn` with the provided attributes and object_class.

        Args:
            dn: DN of the object to modify or create.
            attributes:
                Dictionary with attributes to populate in LDAP.
                See:
                * https://ldap3.readthedocs.io/en/latest/add.html and
                * https://ldap3.readthedocs.io/en/latest/modify.html
                For details
            object_class: The object class to set on newly created objects.
            create: Whether to modify or create the object.

        Return:
            The (possibly new) DN for the object.
        """
        if create:
            # The object does not yet exist, thus we must create it
            await self.add_ldap_object(dn, attributes, object_class)
            return dn

        # To avoid spamming server logs with noop changes / empty writes,
        # we compare with current state of the object with the desired state
        # before writing anything.
        # Without this the LDAP / AD server will register lots of empty writes
        # NOTE: This part of the function really should use some sort of ETag
        #       functionality to ensure that the current-state read is the same
        #       state that we are overwriting.
        ldap_object = await self.get_object_by_dn(dn, attributes=set(attributes.keys()))
        old_state = ldap_object.dict()
        old_state.pop("dn")

        # Ensure both state dictionaries are on the same format.
        current_state = ldap_object.dict()
        current_state = {
            key.casefold(): ensure_list(value) for key, value in current_state.items()
        }
        desired_state = {key.casefold(): value for key, value in attributes.items()}

        # Calculate the actual changes that must be written
        ldap_changes = {
            key: value
            for key, value in desired_state.items()
            if key not in current_state or current_state[key] != value
        }
        ldap_uuid = await self.get_ldap_unique_ldap_uuid(dn)
        await self.modify_ldap_object(dn, ldap_changes, old_state)
        return await self.get_ldap_dn(ldap_uuid)

    async def add_ldap_object(
        self, dn: DN, attributes: dict[str, list], object_class: str
    ) -> None:
        """
        Add an object at `dn` with the provided attributes and object_class.

        Args:
            dn: DN of the object to create.
            attributes:
                Dictionary with attributes to populate in LDAP.
                See:
                * https://ldap3.readthedocs.io/en/latest/add.html and
                * https://ldap3.readthedocs.io/en/latest/modify.html
                For details
            object_class:
                The object class to set on newly created objects.
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

        logger.info(
            "Adding entity to LDAP",
            dn=dn,
            attributes=attributes,
            object_class=object_class,
        )
        _, result = await self.ldap_connection.ldap_add(
            dn,
            object_class,
            attributes=attributes,
        )
        logger.info("LDAP Result", result=result, dn=dn)

    async def get_ldap_unique_ldap_uuid(self, dn: DN) -> LDAPUUID:
        """
        Given a DN, find the unique_ldap_uuid
        """
        logger.info("Looking for LDAP object", dn=dn)
        ldap_object = await self.get_object_by_dn(
            dn, {self.settings.ldap_unique_id_field}
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

        ldap_object = await self.get_object_by_dn(
            dn, {self.settings.ldap_cpr_attribute}
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
            search_results = await object_search(searchParameters, self.connection)
        except LDAPNoSuchObjectResult:
            return set()
        ldap_objects: list[LdapObject] = [
            await make_ldap_object(search_result, self.connection)
            for search_result in search_results
        ]
        dns = {obj.dn for obj in ldap_objects}
        logger.info("Found LDAP(s) object", dns=dns)
        return set(dns)

    async def modify_ldap_object(
        self,
        dn: DN,
        requested_changes: dict[str, list],
        old_state: dict[str, Any] | None = None,
    ) -> None:
        """
        Modify the object at `dn` to ensure it has the provided attributes.

        Args:
            dn: DN of the object to modify.
            requested_changes:
                Dictionary with attributes to populate in LDAP.
                See:
                * https://ldap3.readthedocs.io/en/latest/add.html and
                * https://ldap3.readthedocs.io/en/latest/modify.html
                For details
            old_state:
                Optional dictionary of attributes describing the current state of the
                object at `dn` for use in conditional writes, i.e. to ensure the changes
                in `requested_changes` are only written if the old state matches.
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

        controls: list[tuple[str, bool, Any]] = []
        if old_state:
            assertion_filter = construct_assertion_control_filter(old_state)
            assertion_tuple = construct_assertion_control(assertion_filter)
            controls.append(assertion_tuple)

        logger.info("Uploading object", dn=dn, requested_changes=requested_changes)

        # The fields of the DN cannot be changed using LDAP's modify(), but
        # must instead be changed using modify_dn(). We normalise casing since
        # Microsoft AD is case-insensitive, so attributes written do not
        # necessarily match attributes read as part of the DN.
        modify_dn_attributes = {
            key.casefold(): value for key, value in safe_rdn(dn, decompose=True)
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
                _, result = await self.ldap_connection.ldap_modify(dn, modify_changes)
                logger.info("LDAP Result", result=result, dn=dn)
            except LDAPInvalidValueError as exc:
                logger.exception("LDAP modify failed", dn=dn, changes=requested_changes)
                raise exc

        # MODIFY-DN
        # Calculate our desired DN, based on the current DN + the requested_changes
        desired_rdn_dict = modify_dn_attributes.copy()
        desired_rdn_dict.update(
            {
                key: escape_rdn(one(value))
                for key, value in requested_changes.items()
                if key.casefold() in desired_rdn_dict
            }
        )
        # If the desired DN is what we already have, there is nothing left for us to do
        if desired_rdn_dict == modify_dn_attributes:
            logger.info("Updating DN is not required")
            return

        # Combine the dict to construct the new RDN
        new_rdn_pairs = [f"{key}={value}" for key, value in desired_rdn_dict.items()]
        new_rdn = "+".join(new_rdn_pairs)
        try:
            # Modify LDAP-DN
            logger.info("Changing object RDN", dn=dn, new_rdn=new_rdn)
            # TODO: Use Assertion Control here
            _, result = await self.ldap_connection.ldap_modify_dn(dn, new_rdn)
            logger.info("LDAP Result", result=result, dn=dn)
        except LDAPInvalidValueError as exc:  # pragma: no cover
            logger.exception("LDAP modify-dn failed", dn=dn, changes=requested_changes)
            raise exc

    async def get_object_by_dn(
        self, dn: DN, attributes: set | None = None
    ) -> LdapObject:
        return await get_ldap_object(
            self.ldap_connection.connection, dn, attributes, nest=False
        )

    async def get_attribute_by_dn(self, dn: DN, attribute: str) -> Any:
        ldap_object = await self.get_object_by_dn(dn, {attribute})
        return getattr(ldap_object, attribute)

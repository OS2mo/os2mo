# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Dataloaders to bulk requests."""

import asyncio
from contextlib import suppress
from typing import cast
from uuid import UUID

import structlog
from fastramqpi.ramqp.utils import RequeueMessage
from more_itertools import one
from more_itertools import partition

from .config import Settings
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .ldap import apply_discriminator
from .ldap import filter_dns
from .ldap import is_uuid
from .ldapapi import LDAPAPI
from .moapi import MOAPI
from .models import ITUser
from .types import DN
from .types import LDAPUUID
from .types import CPRNumber
from .types import EmployeeUUID

logger = structlog.stdlib.get_logger()


class NoGoodLDAPAccountFound(ValueError):
    pass


def extract_unique_ldap_uuids(it_users: list[ITUser]) -> set[LDAPUUID]:
    """
    Extracts unique ldap uuids from a list of it-users
    """
    it_user_keys = {ituser.user_key for ituser in it_users}
    not_uuids, uuids = partition(is_uuid, it_user_keys)
    not_uuid_set = set(not_uuids)
    if not_uuid_set:
        logger.warning("Non UUID IT-user user-keys", user_keys=not_uuid_set)
        raise ExceptionGroup(
            "Exceptions during IT-user UUID extraction",
            [
                ValueError(f"Non UUID IT-user user-key: {user_key}")
                for user_key in not_uuid_set
            ],
        )
    # TODO: Check for duplicates?
    return set(map(LDAPUUID, uuids))


class DataLoader:
    def __init__(
        self, settings: Settings, moapi: MOAPI, ldapapi: LDAPAPI, username_generator
    ) -> None:
        self.settings = settings
        self.ldapapi = ldapapi
        self.moapi = moapi
        self.username_generator = username_generator

    async def find_mo_employee_uuid_via_cpr_number(self, dn: DN) -> set[EmployeeUUID]:
        cpr_number = await self.ldapapi.dn2cpr(dn)
        if cpr_number is None:
            return set()
        return await self.moapi.cpr2uuids(cpr_number)

    async def find_mo_employee_uuid(self, dn: DN) -> EmployeeUUID | None:
        cpr_results = await self.find_mo_employee_uuid_via_cpr_number(dn)
        if len(cpr_results) == 1:
            uuid = one(cpr_results)
            logger.info("Found employee via CPR matching", dn=dn, uuid=uuid)
            return uuid

        unique_uuid = await self.ldapapi.get_ldap_unique_ldap_uuid(dn)
        ituser_results = await self.moapi.find_mo_employee_uuid_via_ituser(unique_uuid)
        if len(ituser_results) == 1:
            uuid = one(ituser_results)
            logger.info("Found employee via ITUser matching", dn=dn, uuid=uuid)
            return uuid

        # TODO: Return an ExceptionGroup with both
        # NOTE: This may break a lot of things, because we explicitly match against MultipleObjectsReturnedException
        if len(cpr_results) > 1:
            raise MultipleObjectsReturnedException(f"Multiple CPR matches for dn={dn}")

        if len(ituser_results) > 1:
            raise MultipleObjectsReturnedException(
                f"Multiple ITUser matches for dn={dn}"
            )

        logger.info("No matching employee", dn=dn)
        return None

    async def find_mo_employee_dn_by_itsystem(self, uuid: UUID) -> set[DN]:
        """Tries to find the LDAP DNs belonging to a MO employee via ITUsers.

        Args:
            uuid: UUID of the employee to try to find DNs for.

        Returns:
            A potentially empty set of DNs.
        """
        # TODO: How do we know if the ITUser is up-to-date with the newest DNs in AD?

        # The ITSystem only exists if configured to do so
        raw_it_system_uuid = await self.moapi.get_ldap_it_system_uuid()
        # If it does not exist, we cannot fetch users for it
        if raw_it_system_uuid is None:
            return set()

        it_system_uuid = UUID(raw_it_system_uuid)
        it_users = await self.moapi.load_mo_employee_it_users(uuid, it_system_uuid)
        ldap_uuids = extract_unique_ldap_uuids(it_users)
        uuid_dn_map = await self.ldapapi.convert_ldap_uuids_to_dns(ldap_uuids)
        dns = set(uuid_dn_map.values())
        dns.discard(None)
        # No DNs, no problem
        if not dns:
            return set()

        # If we have one or more ITUsers (with valid dns), return those
        logger.info(
            "Found DN(s) using ITUser lookup",
            dns=dns,
            employee_uuid=uuid,
        )
        return cast(set[DN], dns)

    async def find_mo_employee_dn_by_cpr_number(self, uuid: UUID) -> set[DN]:
        """Tries to find the LDAP DNs belonging to a MO employee via CPR numbers.

        Args:
            uuid: UUID of the employee to try to find DNs for.

        Returns:
            A potentially empty set of DNs.
        """
        # If the employee has a cpr-no, try using that to find matchind DNs
        employee = await self.moapi.load_mo_employee(uuid)
        if employee is None:
            raise NoObjectsReturnedException(f"Unable to lookup employee: {uuid}")
        cpr_number = CPRNumber(employee.cpr_number) if employee.cpr_number else None
        # No CPR, no problem
        if not cpr_number:
            return set()

        logger.info(
            "Attempting CPR number lookup",
            employee_uuid=uuid,
        )
        dns = set()
        with suppress(NoObjectsReturnedException):
            dns = await self.ldapapi.cpr2dns(cpr_number)
        if not dns:
            return set()
        logger.info(
            "Found DN(s) using CPR number lookup",
            dns=dns,
            employee_uuid=uuid,
        )
        return dns

    async def find_mo_employee_dn(self, uuid: UUID) -> set[DN]:
        """Tries to find the LDAP DNs belonging to a MO employee.

        Args:
            uuid: UUID of the employee to try to find DNs for.

        Returns:
            A potentially empty set of DNs.
        """
        # TODO: This should probably return a list of EntityUUIDs rather than DNs
        #       However this should probably be a change away from DNs in general
        logger.info("Attempting to find DNs", employee_uuid=uuid)
        # TODO: We should be able to trust just the ITUsers, however we do not.
        #       Maybe once the code becomes easier to reason about, we can get to that.
        #       But for now, we fetch all accounts, and use the discriminator.
        #
        # TODO: We may want to expand this in the future to also check for half-created
        #       objects, to support scenarios where the application may crash after
        #       creating an LDAP account, but before making a MO ITUser.
        ituser_dns, cpr_number_dns = await asyncio.gather(
            self.find_mo_employee_dn_by_itsystem(uuid),
            self.find_mo_employee_dn_by_cpr_number(uuid),
        )
        dns = ituser_dns | cpr_number_dns
        if dns:
            logger.info("Found DNs for MO employee", employee_uuid=uuid, dns=dns)
            return dns
        logger.warning("Unable to find DNs for MO employee", employee_uuid=uuid)
        return set()

    async def make_mo_employee_dn(
        self, uuid: UUID, common_name: str | None = None
    ) -> DN:
        employee = await self.moapi.load_mo_employee(uuid)
        if employee is None:
            raise NoObjectsReturnedException(f"Unable to lookup employee: {uuid}")
        cpr_number = CPRNumber(employee.cpr_number) if employee.cpr_number else None

        # Check if we even dare create a DN, we need a correlation key before we dare
        if cpr_number is None:
            raw_it_system_uuid = await self.moapi.get_ldap_it_system_uuid()
            if raw_it_system_uuid is None:
                logger.warning(
                    "Refused to generate a DN for employee (no correlation key)",
                    employee_uuid=uuid,
                )
                raise RequeueMessage(
                    "Unable to generate DN, no correlation key available"
                )

        logger.info("Generating DN for user", employee_uuid=uuid)
        if common_name is None:
            common_name = await self.username_generator.generate_common_name(employee)
        dn = await self.username_generator.generate_dn(common_name)
        assert isinstance(dn, str)
        return dn

    async def _find_best_dn(self, uuid: EmployeeUUID) -> DN | None:
        dns = await self.find_mo_employee_dn(uuid)
        dns = await filter_dns(self.settings, self.ldapapi.connection, dns)
        # If we found DNs, we want to synchronize to the best of them
        if not dns:
            return None
        logger.info("Found DNs for user", dns=dns, uuid=uuid)
        best_dn = await apply_discriminator(self.settings, self.ldapapi.connection, dns)
        # If no good LDAP account was found, we do not want to synchronize at all
        if not best_dn:
            logger.warning(
                "Aborting synchronization, as no good LDAP account was found",
                dns=dns,
                uuid=uuid,
            )
            raise NoGoodLDAPAccountFound("Aborting synchronization")
        return best_dn

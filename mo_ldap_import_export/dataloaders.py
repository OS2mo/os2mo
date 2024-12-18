# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Dataloaders to bulk requests."""

import asyncio
from contextlib import suppress
from uuid import UUID

import structlog
from fastramqpi.context import Context
from ldap3 import Connection
from more_itertools import one
from more_itertools import partition

from .config import Settings
from .exceptions import DNNotFound
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .ldap import is_uuid
from .ldapapi import LDAPAPI
from .moapi import MOAPI
from .models import ITUser
from .types import DN
from .types import CPRNumber
from .types import EmployeeUUID
from .utils import mo_today

logger = structlog.stdlib.get_logger()


class DataLoader:
    def __init__(self, context: Context, settings: Settings, moapi: MOAPI) -> None:
        self.context = context
        self.user_context = context["user_context"]
        self.ldap_connection: Connection = self.user_context["ldap_connection"]
        self.settings = settings
        self.ldapapi = LDAPAPI(self.settings, self.ldap_connection)
        self.moapi = moapi

        from .usernames import get_username_generator_class

        logger.info("Initializing username generator")
        username_generator_class = get_username_generator_class(
            self.settings.conversion_mapping.username_generator.objectClass
        )
        self.username_generator = username_generator_class(
            self.settings,
            self,
            self.ldap_connection,
        )

    async def find_mo_employee_uuid_via_cpr_number(self, dn: str) -> set[EmployeeUUID]:
        cpr_number = await self.ldapapi.dn2cpr(dn)
        if cpr_number is None:
            return set()

        result = await self.moapi.graphql_client.read_employee_uuid_by_cpr_number(
            cpr_number
        )
        return {EmployeeUUID(employee.uuid) for employee in result.objects}

    async def find_mo_employee_uuid(self, dn: str) -> EmployeeUUID | None:
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

    def extract_unique_ldap_uuids(self, it_users: list[ITUser]) -> set[UUID]:
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
        return set(map(UUID, uuids))

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
        ldap_uuids = self.extract_unique_ldap_uuids(it_users)
        dns = await self.ldapapi.convert_ldap_uuids_to_dns(ldap_uuids)
        # No DNs, no problem
        if not dns:
            return set()

        # If we have one or more ITUsers (with valid dns), return those
        logger.info(
            "Found DN(s) using ITUser lookup",
            dns=dns,
            employee_uuid=uuid,
        )
        return dns

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
        logger.info(
            "Attempting to find DNs",
            employee_uuid=uuid,
        )
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
            return dns
        logger.warning(
            "Unable to find DNs for MO employee",
            employee_uuid=uuid,
        )
        return set()

    # TODO: move to synctool
    async def make_mo_employee_dn(self, uuid: UUID) -> DN:
        employee = await self.moapi.load_mo_employee(uuid)
        if employee is None:
            raise NoObjectsReturnedException(f"Unable to lookup employee: {uuid}")
        cpr_number = CPRNumber(employee.cpr_number) if employee.cpr_number else None

        # Check if we even dare create a DN
        raw_it_system_uuid = await self.moapi.get_ldap_it_system_uuid()
        if raw_it_system_uuid is None and cpr_number is None:
            logger.warning(
                "Could not or generate a DN for employee (cannot correlate)",
                employee_uuid=uuid,
            )
            raise DNNotFound("Unable to generate DN, no correlation key available")

        # If we did not find a DN neither via ITUser nor via CPR-number, then we want
        # to create one, by generating a DN, importing the user and potentially creating
        # a binding between the two.

        logger.info("Generating DN for user", employee_uuid=uuid)
        # NOTE: This not only generates the DN as the name suggests,
        #       rather it also *creates it in LDAP*, be warned!
        #
        #       Additionally it turns out that it does not only create the DN in LDAP
        #       rather it uploads the entire employee object to LDAP.
        #
        # TODO: Does this upload actively require a cpr_number on the employee?
        #       If we do not have the CPR number nor the ITSystem, we would be leaking
        #       the DN we generate, so maybe we should guard for this, the old code seemed
        #       to do so, maybe we should simply not upload anything in that case.
        dn = await self.username_generator.generate_dn(employee)
        assert isinstance(dn, str)

        # If the LDAP ITSystem exists, we want to create a binding to our newly
        # generated (and created) DN, such that it can be correlated in the future.
        #
        # NOTE: This may not be executed if the program crashes after the above line,
        #       thus the current code is not robust and may fail at any time.
        #       The appropriate solution here is to ensure that generate_dn atomically
        #       creates a link between the MO entity and the newly created LDAP entity,
        #       such as by adding the MO UUID to the newly created LDAP entity.
        if raw_it_system_uuid is not None:
            logger.info(
                "No ITUser found, creating one to correlate with DN",
                employee_uuid=uuid,
                dn=dn,
            )
            # Get its unique ldap uuid
            # TODO: Get rid of this code and operate on EntityUUIDs thoughout
            unique_uuid = await self.ldapapi.get_ldap_unique_ldap_uuid(dn)
            logger.info(
                "LDAP UUID found for DN",
                employee_uuid=uuid,
                dn=dn,
                ldap_uuid=unique_uuid,
            )
            # Make a new it-user
            it_user = ITUser(
                user_key=str(unique_uuid),
                itsystem=UUID(raw_it_system_uuid),
                person=uuid,
                validity={"start": mo_today()},
            )
            await self.moapi.create_ituser(it_user)

        return dn

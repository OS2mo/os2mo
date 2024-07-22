# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import structlog
from fastramqpi.context import Context
from fastramqpi.depends import UserContext

from .converters import LdapConverter
from .converters import get_it_system_uuid
from .dataloaders import DataLoader
from .exceptions import IgnoreChanges
from .ldap import check_ou_in_list_of_ous
from .utils import extract_ou_from_dn

logger = structlog.stdlib.get_logger()


class ExportChecks:
    """
    Class with modules that are invoked when exporting data to LDAP
    """

    def __init__(self, context: Context):
        self.context = context
        self.user_context: UserContext = self.context["user_context"]
        self.dataloader: DataLoader = self.user_context["dataloader"]
        self.converter: LdapConverter = self.user_context["converter"]

    async def check_alleroed_sd_number(self, employee_uuid: UUID, object_uuid: UUID):
        """
        Checks if an SD-employee number starts with 9 and aborts if so.

        These numbers belong to 'timelønnede' in Allerød Kommune, and should not be
        exported to AD.

        Notes
        -------
        For Allerød, SD-Numbers are stored inside Engagements on the user_key attribute
        """

        error_message = (
            f"SD-number for employee with uuid = '{employee_uuid}' starts with '9'."
        )

        engagements = await self.dataloader.load_mo_employee_engagements(employee_uuid)

        sd_numbers = [e.user_key for e in engagements]
        hourly_paid_worker = [sd_number.startswith("9") for sd_number in sd_numbers]
        engagement_dict = {e.uuid: e.user_key for e in engagements}

        if not hourly_paid_worker:
            # Nothing to do if there are no engagements
            return
        elif all(hourly_paid_worker):
            # If this is an hourly paid worker, ignore him
            raise IgnoreChanges(error_message)
        elif any(hourly_paid_worker):
            # If the hourly paid worker also has other engagements;
            # Only ignore the specific engagement which states that he is hourly paid
            if engagement_dict.get(object_uuid, "").startswith("9"):
                raise IgnoreChanges(error_message)

    async def check_it_user(self, employee_uuid: UUID, it_system_user_key: str):
        if not it_system_user_key:
            return

        it_system_uuid = await get_it_system_uuid(
            self.dataloader.graphql_client, it_system_user_key
        )
        it_users = await self.dataloader.load_mo_employee_it_users(
            employee_uuid, UUID(it_system_uuid)
        )

        if not it_users:
            raise IgnoreChanges(
                f"employee with uuid = {employee_uuid} "
                f"does not have an it-user with user_key = {it_system_user_key}"
            )


class ImportChecks:
    def __init__(self, context: Context):
        self.context = context

    async def check_holstebro_ou_is_externals_issue_57426(
        self, ou_includes: list[str], current_dn: str, json_key: str
    ) -> bool:
        """
        Raise IgnoreChanges if current_dn's OU is not in any of ou_includes.

        Never raise if json_key==Custom as Holstebro want to import job
        functions for everyone regardless of OU.
        """
        # Holstebro needs stillingsbetegnelser regardless of OU
        if json_key == "Custom":
            return True

        # Check that current_dn's OU is in one of the accepted OU's
        current_ou = extract_ou_from_dn(current_dn)
        try:
            check_ou_in_list_of_ous(current_ou, ou_includes)
        except ValueError:
            logger.info(
                "Check Holstebro OU is externals failed",
                current_ou=current_ou,
                ou_includes=ou_includes,
                json_key=json_key,
                exc_info=True,
            )
            return False
        return True

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import structlog

from mo_ldap_import_export.types import DN

from .dataloaders import DataLoader
from .exceptions import IgnoreChanges
from .ldap import check_ou_in_list_of_ous
from .utils import extract_ou_from_dn

logger = structlog.stdlib.get_logger()


class ExportChecks:
    """
    Class with modules that are invoked when exporting data to LDAP
    """

    def __init__(self, dataloader: DataLoader) -> None:
        self.dataloader = dataloader

    async def check_it_user(self, employee_uuid: UUID, it_system_user_key: str):
        if not it_system_user_key:
            return

        it_system_uuid = await self.dataloader.moapi.get_it_system_uuid(
            it_system_user_key
        )
        it_users = await self.dataloader.moapi.load_mo_employee_it_users(
            employee_uuid, UUID(it_system_uuid)
        )

        if not it_users:
            raise IgnoreChanges(
                f"employee with uuid = {employee_uuid} "
                f"does not have an it-user with user_key = {it_system_user_key}"
            )


class ImportChecks:
    async def check_holstebro_ou_is_externals_issue_57426(
        self, ou_includes: list[str], current_dn: DN, json_key: str
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

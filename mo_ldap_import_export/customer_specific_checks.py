# -*- coding: utf-8 -*-
from fastramqpi.context import Context

from .exceptions import IgnoreChanges


class ExportChecks:
    """
    Class with modules that are invoked when exporting data to LDAP
    """

    def __init__(self, context: Context):
        self.context = context
        self.user_context = self.context["user_context"]
        self.dataloader = self.user_context["dataloader"]
        self.converter = self.user_context["converter"]

    async def check_alleroed_sd_number(self, employee_uuid):
        """
        Checks if an SD-employee number starts with 9 and aborts if so.

        These numbers belong to 'timelønnede' in Allerød Kommune, and should not be
        exported to AD.

        Notes
        -------
        For Allerød, SD-Numbers are stored inside Engagements on the user_key attribute
        """

        engagements = await self.dataloader.load_mo_employee_engagements(employee_uuid)
        sd_numbers = [e.user_key for e in engagements]

        for sd_number in sd_numbers:
            if sd_number.startswith("9"):
                raise IgnoreChanges(
                    (
                        "[check_sd_number] SD-number for employee with "
                        f"uuid = '{employee_uuid}' starts with '9'."
                    )
                )

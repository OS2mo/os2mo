# -*- coding: utf-8 -*-
from uuid import UUID

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
            "[check_sd_number] SD-number for employee with "
            f"uuid = '{employee_uuid}' starts with '9'."
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

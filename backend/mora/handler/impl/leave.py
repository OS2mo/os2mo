# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import logging
from asyncio import create_task

from mora import lora
from .engagement import EngagementReader
from .. import reading
from ... import mapping
from ...request_scoped.query_args import current_query
from ...service import employee
from ...service import facet

ROLE_TYPE = "leave"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class LeaveReader(reading.OrgFunkReadingHandler):
    function_key = mapping.LEAVE_KEY

    @classmethod
    async def _get_mo_object_from_effect(cls, effect, start, end, funcid):
        person = mapping.USER_FIELD.get_uuid(effect)
        leave_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        engagement_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)

        base_obj = create_task(
            super()._get_mo_object_from_effect(effect, start, end, funcid))
        only_primary_uuid = current_query.args.get('only_primary_uuid')

        person_task = create_task(
            employee.request_bulked_get_one_employee(
                person,
                only_primary_uuid=only_primary_uuid))

        leave_type_task = create_task(facet.request_bulked_get_one_class(
            leave_type,
            only_primary_uuid=only_primary_uuid))

        if only_primary_uuid:
            engagement = {mapping.UUID: engagement_uuid}
        else:
            # We look up whatever engagement is active at the present time period
            # to account for edge cases where the engagement might have changed or is
            # no longer active during the time period
            present_connector = lora.Connector(validity="present")
            engagements_task = create_task(EngagementReader.get(
                present_connector, {"uuid": [engagement_uuid]}
            ))
            engagements = await engagements_task
            if len(engagements) == 0:
                logger.warning(f"Engagement {engagement_uuid} returned no results")
                engagement = None
            else:
                if len(engagements) > 1:
                    logger.warning(
                        f"Engagement {engagement_uuid} returned more than one result"
                    )
                engagement = engagements[0]

        r = {
            **await base_obj,
            mapping.PERSON: await person_task,
            mapping.LEAVE_TYPE: await leave_type_task,
            mapping.ENGAGEMENT: engagement,
        }

        return r

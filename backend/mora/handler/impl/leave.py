# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import flask
import logging
from mora import lora

from .engagement import EngagementReader
from .. import reading
from ... import common
from ... import mapping
from ...service import employee
from ...service import facet

ROLE_TYPE = "leave"

logger = logging.getLogger(__name__)


@reading.register(ROLE_TYPE)
class LeaveReader(reading.OrgFunkReadingHandler):
    function_key = mapping.LEAVE_KEY

    @classmethod
    def get_mo_object_from_effect(cls, effect, start, end, funcid):
        c = common.get_connector()

        person = mapping.USER_FIELD.get_uuid(effect)
        leave_type = mapping.ORG_FUNK_TYPE_FIELD.get_uuid(effect)
        engagement_uuid = mapping.ASSOCIATED_FUNCTION_FIELD.get_uuid(effect)

        only_primary_uuid = flask.request.args.get("only_primary_uuid")
        if only_primary_uuid:
            engagement = {mapping.UUID: engagement_uuid}
        else:
            # We look up whatever engagement is active at the present time period
            # to account for edge cases where the engagement might have changed or is
            # no longer active during the time period
            present_connector = lora.Connector(validity="present")
            engagements = EngagementReader.get(
                present_connector, {"uuid": [engagement_uuid]}
            )
            if len(engagements) == 0:
                logger.warning(f"Engagement {engagement_uuid} returned no results")
                engagement = None
            else:
                if len(engagements) > 1:
                    logger.warning(
                        f"Engagement {engagement_uuid} returned more than one result"
                    )
                engagement = engagements[0]

        base_obj = super().get_mo_object_from_effect(effect, start, end, funcid)

        r = {
            **base_obj,
            mapping.PERSON: employee.get_one_employee(c, person),
            mapping.LEAVE_TYPE: facet.get_one_class(c, leave_type),
            mapping.ENGAGEMENT: engagement,
        }

        return r

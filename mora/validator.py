#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import datetime
from mora import lora
from mora import util

ERRORS = {
    'create_org_unit': {
        'errors': [
            {
                'key not used': 'Denne enheds gyldighedsperiode er ikke '
                                'indeholdt i overenhedens gyldighedsperiode'
            }
        ]
    },
    'rename_org_unit': {
        'errors': [
            {
                'key not used': 'Ulovlig overenhed'
            }
        ]
    }
}


def _is_date_range_valid(parent: str, startdate: str, enddate: str) -> bool:
    """
    Determine if the given dates are within validity of the parent unit
    :param parent: The UUID of the parent unit
    :param startdate:
    :param enddate:
    :return:
    """

    assert util.parsedatetime(startdate) < util.parsedatetime(enddate)

    parent = lora.organisationenhed.get(
        uuid=parent,
        virkningfra=util.to_lora_time(startdate),
        virkningtil=util.to_lora_time(enddate),
    )

    validity = parent['tilstande']['organisationenhedgyldighed']

    if len(validity) == 1 and validity[0]['gyldighed'] == 'Aktiv':
        return True

    return False


def is_create_org_unit_request_valid(req: dict) -> bool:
    startdate = req['valid-from']
    enddate = req.get('valid-to', 'infinity')
    parent = req['parent']
    return _is_date_range_valid(parent, startdate, enddate)


def is_candidate_parent_valid(unitid: str, req: dict) -> bool:
    """
    For moving an org unit. Check if the candidate parent is in the subtree of
    the org unit itself. Note: it is (and should be) allowed to move an org
    unit to its own parent - since it can be moved back and forth on different
    dates
    :param unitid: the UUID of the current org unit
    :param req: the frontend request
    :return: True if the candidate parent is valid and False otherwise
    """

    from_ = util.parsedatetime(req['moveDate']) + datetime.timedelta(hours=12)
    to = util.parsedatetime(req['moveDate']) + datetime.timedelta(hours=13)

    # Do not allow moving of the root org unit
    org_unit_relations = lora.organisationenhed.get(
        uuid=unitid,
        virkningfra=from_.isoformat(),
        virkningtil=to.isoformat()
    )['relationer']
    if org_unit_relations['overordnet'][0]['uuid'] == \
            org_unit_relations['tilhoerer'][0]['uuid']:
        return False

    # Org unit is to the root org unit
    def is_node_valid(node_uuid: str) -> bool:
        if node_uuid == unitid:
            return False

        node_relations = lora.organisationenhed.get(
            uuid=node_uuid,
            virkningfra=from_.isoformat(),
            virkningtil=to.isoformat()
        )['relationer']

        parent = node_relations['overordnet'][0]['uuid']
        if parent == node_relations['tilhoerer'][0]['uuid']:
            # Root org unit
            return True

        return is_node_valid(parent)

    return is_node_valid(req['newParentOrgUnitUUID'])

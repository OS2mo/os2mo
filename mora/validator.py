#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import datetime
from mora import exceptions
from mora import lora
from mora import util
from .service import common
from .service import keys


def _is_date_range_valid(parent: str, startdate: datetime.datetime,
                         enddate: datetime.datetime, lora_scope,
                         gyldighed_key: str) -> bool:
    """
    Determine if the given dates are within validity of the parent unit.

    :param parent: The UUID of the parent unit.
    :param startdate: The candidate start date.
    :param enddate: The candidate end date.
    :param lora_scope: A scope object from a LoRa connector.
    :param gyldighed_key: The key of where to find the 'gyldighed' in the
        object in question
    :return: True if the date range is valid and false otherwise.
    """

    if startdate >= enddate:
        return False

    previous_end = None

    for start, end, effect in lora_scope.get_effects(
        parent,
        {
            'tilstande': (
                gyldighed_key,
            )
        }
    ):
        if previous_end is None:
            # initial case
            if startdate < start:
                # start is too late!
                return False
        elif start != previous_end:
            # non-consecutive chunk - so not valid for that time
            return False

        vs = effect['tilstande'][gyldighed_key]

        if not vs or any(v['gyldighed'] != 'Aktiv' for v in vs):
            # not valid for the given time
            return False

        previous_end = end

    # verify that we've achieved full coverage - and return a bool
    return previous_end is not None and previous_end >= enddate


def is_date_range_in_org_unit_range(org_unit_uuid, valid_from, valid_to):
    scope = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to)
    ).organisationenhed
    gyldighed_key = "organisationenhedgyldighed"

    if not _is_date_range_valid(org_unit_uuid, valid_from, valid_to, scope,
                                gyldighed_key):
        raise exceptions.ValidationError(
            'Date range exceeds validity range of '
            'associated organisational unit.')


def is_date_range_in_employee_range(employee_uuid, valid_from, valid_to):
    scope = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to)
    ).bruger
    gyldighed_key = "brugergyldighed"

    if not _is_date_range_valid(employee_uuid, valid_from, valid_to, scope,
                                gyldighed_key):
        raise exceptions.ValidationError(
            'Date range exceeds validity range of associated employee.')


def is_candidate_parent_valid(unitid: str, req: dict) -> bool:
    """
    For moving an org unit. Check if the candidate parent is in the subtree of
    the org unit itself. Note: it is (and should be) allowed to move an org
    unit to its own parent - since it can be moved back and forth on different
    dates.

    :param unitid: The UUID of the current org unit.
    :param req: The frontend request.
    :return: True if the candidate parent is valid and False otherwise.
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

    # Use for checking that the candidate parent is not the units own subtree
    def is_node_valid(node_uuid: str) -> bool:
        if node_uuid == unitid:
            return False

        node = lora.organisationenhed.get(
            uuid=node_uuid,
            virkningfra=from_.isoformat(),
            virkningtil=to.isoformat()
        )

        # Check that the node is not inactive
        if node['tilstande']['organisationenhedgyldighed'][0]['gyldighed'] == \
                'Inaktiv':
            return False

        node_relations = node['relationer']
        parent = node_relations['overordnet'][0]['uuid']
        if parent == node_relations['tilhoerer'][0]['uuid']:
            # Root org unit
            return True

        return is_node_valid(parent)

    return is_node_valid(req['newParentOrgUnitUUID'])


def _get_org_unit_endpoint_date(org_unit: dict,
                                enddate=True) -> datetime.datetime:
    """
    Get the validity start date or end date for an org unit (pre-condition:
    the org unit has exactly one active period.

    :param org_unit: The org unit to get the end-point date from.
    :param enddate: If true (default) the enddate will be used as the end-point
        date.
    """
    for g in org_unit['tilstande']['organisationenhedgyldighed']:
        if g['gyldighed'] == 'Aktiv':
            virkning = g['virkning']
            if enddate:
                return util.parsedatetime(virkning['to'])
            else:
                return util.parsedatetime(virkning['from'])

    raise exceptions.ValidationError('the unit did not have an end date!')


def is_inactivation_date_valid(unitid: str, end_date: str) -> bool:
    """
    Check if the inactivation date is valid.

    :param unitid: The UUID of the org unit.
    :param end_date: The candidate end-date.
    :return: True if the inactivation date is valid and false otherwise.
    """
    candidate_enddate = util.parsedatetime(end_date)

    # Check that the end date is greater than the start date of the org unit
    org_unit = lora.get_org_unit(unitid)
    if candidate_enddate <= _get_org_unit_endpoint_date(org_unit, False):
        return False

    # Check that the end dates of the children smaller than org unit end date
    children = lora.organisationenhed(overordnet=unitid)
    for child in children:
        child_unit = lora.get_org_unit(child)
        if candidate_enddate < _get_org_unit_endpoint_date(child_unit):
            return False

    return True

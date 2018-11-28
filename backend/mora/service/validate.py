#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


import flask

from .. import validator
from .. import util
from .. import mapping

blueprint = flask.Blueprint('validate', __name__, static_url_path='',
                            url_prefix='/validate')


@blueprint.route('/org-unit/', methods=['POST'])
def candidate_org_unit():
    """
    Verify that an org unit and a set of start/end dates are compatible
    """
    req = flask.request.get_json()

    org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT, required=True)
    valid_from, valid_to = util.get_validities(req)

    validator.is_date_range_in_org_unit_range(
        org_unit_uuid, valid_from, valid_to)

    return flask.jsonify(success=True)


@blueprint.route('/employee/', methods=['POST'])
def candidate_employee():
    """
    Verify that an employee and a set of start/end dates are compatible
    """
    req = flask.request.get_json()

    employee = util.checked_get(req, mapping.PERSON, {}, required=True)
    valid_from, valid_to = util.get_validities(req)

    validator.is_date_range_in_employee_range(employee, valid_from, valid_to)

    return flask.jsonify(success=True)


@blueprint.route('/cpr/')
def check_cpr():
    """
    Verify that an employee with the given CPR no. does not already exist
    in the database
    """
    req = flask.request.get_json()

    cpr = util.checked_get(req, mapping.CPR_NO, "", required=True)
    valid_from, valid_to = util.get_validities(req)
    org_uuid = util.get_mapping_uuid(req, mapping.ORG, required=True)

    validator.does_employee_with_cpr_already_exist(
        cpr, valid_from, valid_to, org_uuid)

    return flask.jsonify(success=True)


@blueprint.route('/active-engagements/')
def employee_engagements():
    """
    Verify that an employee has active engagements
    """
    req = flask.request.get_json()

    employee_uuid = util.get_mapping_uuid(req, mapping.PERSON, required=True)
    valid_from, valid_to = util.get_validities(req)

    validator.does_employee_have_active_engagement(
        employee_uuid, valid_from, valid_to)

    return flask.jsonify(success=True)


@blueprint.route('/existing-associations/')
def employee_existing_associations():
    """
    Verify that an employee does not have active associations
    """
    req = flask.request.get_json()

    employee_uuid = util.get_mapping_uuid(req, mapping.PERSON, required=True)
    org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT, required=True)
    valid_from, valid_to = util.get_validities(req)

    validator.does_employee_have_existing_association(
        employee_uuid, org_unit_uuid, valid_from, valid_to)

    return flask.jsonify(success=True)

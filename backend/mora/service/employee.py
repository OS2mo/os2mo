#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''
Employees
---------

This section describes how to interact with employees.

For more information regarding reading relations involving employees, refer to
:http:get:`/service/(any:type)/(uuid:id)/details/`

'''
import copy
import uuid
import enum
import json

import flask

from . import handlers
from . import org
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import settings
from .. import util
from .. import validator

blueprint = flask.Blueprint('employee', __name__, static_url_path='',
                            url_prefix='/service')


@enum.unique
class EmployeeDetails(enum.Enum):
    # name & userkey only
    MINIMAL = 0

    # with everything except child count
    FULL = 1

    # minimal and integration_data
    INTEGRATION = 2


class EmployeeRequestHandler(handlers.RequestHandler):
    __slots__ = ('details_requests',)
    role_type = "employee"

    def prepare_create(self, req):
        c = lora.Connector()
        name = util.checked_get(req, mapping.NAME, "", required=True)
        integration_data = util.checked_get(
            req,
            mapping.INTEGRATION_DATA,
            {},
            required=False
        )
        org_uuid = util.get_mapping_uuid(req, mapping.ORG, required=True)
        cpr = util.checked_get(req, mapping.CPR_NO, "", required=False)
        userid = util.get_uuid(req, required=False)

        if not userid:
            userid = str(uuid.uuid4())
        try:
            valid_from = \
                util.get_cpr_birthdate(cpr) if cpr else util.NEGATIVE_INFINITY
        except ValueError as exc:
            exceptions.ErrorCodes.V_CPR_NOT_VALID(cpr=cpr, cause=exc)

        userids = c.bruger.fetch(
            tilknyttedepersoner="urn:dk:cpr:person:{}".format(cpr),
            tilhoerer=org_uuid
        )

        if userids and userid not in userids:
            exceptions.ErrorCodes.V_EXISTING_CPR(cpr=cpr)

        valid_to = util.POSITIVE_INFINITY
        bvn = util.checked_get(req, mapping.USER_KEY, str(uuid.uuid4()))

        user = common.create_bruger_payload(
            valid_from=valid_from,
            valid_to=valid_to,
            brugernavn=name,
            brugervendtnoegle=bvn,
            tilhoerer=org_uuid,
            cpr=cpr,
            integration_data=integration_data,
        )

        details = util.checked_get(req, 'details', [])
        details_with_persons = _inject_persons(details, userid, valid_from,
                                               valid_to)
        # Validate the creation requests
        self.details_requests = handlers.generate_requests(
            details_with_persons,
            handlers.RequestType.CREATE
        )

        print(self.details_requests)
        self.payload = user
        self.uuid = userid

    def prepare_edit(self, req: dict):
        original_data = util.checked_get(req, 'original', {}, required=False)
        data = util.checked_get(req, 'data', {}, required=True)
        userid = util.get_uuid(req, required=False)
        if not userid:
            userid = util.get_uuid(data, fallback=original_data)

        # Get the current org-unit which the user wants to change
        c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
        original = c.bruger.get(uuid=userid)
        new_from, new_to = util.get_validities(data)

        validator.is_edit_from_date_before_today(new_from)

        payload = dict()
        if original_data:
            # We are performing an update
            old_from, old_to = util.get_validities(original_data)
            payload = common.inactivate_old_interval(
                old_from, old_to, new_from, new_to, payload,
                ('tilstande', 'brugergyldighed')
            )

            original_uuid = util.get_mapping_uuid(original_data,
                                                  mapping.EMPLOYEE)

            if original_uuid and original_uuid != userid:
                exceptions.ErrorCodes.E_INVALID_INPUT(
                    'cannot change employee uuid!',
                )

        update_fields = list()

        # Always update gyldighed
        update_fields.append((
            mapping.EMPLOYEE_GYLDIGHED_FIELD,
            {'gyldighed': "Aktiv"}
        ))

        if mapping.NAME in data or mapping.INTEGRATION_DATA in data:
            attrs = mapping.EMPLOYEE_EGENSKABER_FIELD.get(original)[-1].copy()

            if mapping.NAME in data:
                attrs['brugernavn'] = data[mapping.NAME]

            if mapping.INTEGRATION_DATA in data:
                attrs['integrationsdata'] = json.dumps(
                    data[mapping.INTEGRATION_DATA]
                )

            update_fields.append((
                mapping.EMPLOYEE_EGENSKABER_FIELD,
                attrs,
            ))

        if mapping.CPR_NO in data:
            attrs = mapping.EMPLOYEE_PERSON_FIELD.get(original)[-1].copy()
            attrs['urn'] = 'urn:dk:cpr:person:{}'.format(data[mapping.CPR_NO])

            update_fields.append((
                mapping.EMPLOYEE_PERSON_FIELD,
                attrs,
            ))

        payload = common.update_payload(new_from, new_to, update_fields,
                                        original, payload)

        bounds_fields = list(
            mapping.EMPLOYEE_FIELDS.difference({x[0] for x in update_fields}))
        payload = common.ensure_bounds(new_from, new_to, bounds_fields,
                                       original, payload)

        self.payload = payload
        self.uuid = userid

    def submit(self):
        c = lora.Connector()

        if self.request_type == handlers.RequestType.CREATE:
            result = c.bruger.create(self.payload, self.uuid)
        else:
            result = c.bruger.update(self.payload, self.uuid)

        # process subrequests, if any
        [r.submit() for r in getattr(self, "details_requests", [])]

        return result


def get_one_employee(c, userid, user=None, details=EmployeeDetails.MINIMAL):
    if not user:
        user = c.bruger.get(userid)

        if not user or not util.is_reg_valid(user):
            return None

    props = user['attributter']['brugeregenskaber'][0]

    r = {
        mapping.NAME: props['brugernavn'],
        mapping.UUID: userid,
    }

    if details is EmployeeDetails.FULL:
        rels = user['relationer']
        orgid = rels['tilhoerer'][0]['uuid']

        if rels.get('tilknyttedepersoner'):
            r[mapping.CPR_NO] = (
                rels['tilknyttedepersoner'][0]['urn'].rsplit(':', 1)[-1]
            )

        r[mapping.ORG] = org.get_one_organisation(c, orgid)
        r[mapping.USER_KEY] = props['brugervendtnoegle']
    elif details is EmployeeDetails.MINIMAL:
        pass  # already done
    elif details is EmployeeDetails.INTEGRATION:
        r[mapping.INTEGRATION_DATA] = props.get("integrationsdata")
    return r


@blueprint.route('/o/<uuid:orgid>/e/')
@util.restrictargs('at', 'start', 'limit', 'query')
def list_employees(orgid):
    '''Query employees in an organisation.

    .. :quickref: Employee; List & search

    :param uuid orgid: UUID of the organisation to search.

    :queryparam date at: Show employees at this point in time,
        in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by employees matching this string.
        Please note that this only applies to attributes of the user, not the
        relations or engagements they have.

    :>json string items: The returned items.
    :>json string offset: Pagination offset.
    :>json string total: Total number of items available on this query.

    :>jsonarr string name: Human-readable name.
    :>jsonarr string uuid: Machine-friendly UUID.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      {
        "items": [
          {
            "name": "Hans Bruger",
            "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3"
          },
          {
            "name": "Joe User",
            "uuid": "cd2dcfad-6d34-4553-9fee-a7023139a9e8"
          }
        ],
        "offset": 0,
        "total": 1
      }

    '''

    # TODO: share code with list_orgunits?

    c = common.get_connector()

    args = flask.request.args

    kwargs = dict(
        limit=int(args.get('limit', 0)) or settings.DEFAULT_PAGE_SIZE,
        start=int(args.get('start', 0)) or 0,
        tilhoerer=orgid,
        gyldighed='Aktiv',
    )

    if 'query' in args:
        if util.is_cpr_number(args['query']):
            kwargs.update(
                tilknyttedepersoner='urn:dk:cpr:person:' + args['query'],
            )
        else:
            kwargs.update(vilkaarligattr='%{}%'.format(args['query']))

    return flask.jsonify(
        c.bruger.paged_get(get_one_employee, **kwargs)
    )


@blueprint.route('/e/<uuid:id>/')
@util.restrictargs('at')
def get_employee(id):
    '''Retrieve an employee.

    .. :quickref: Employee; Get

    :queryparam date at: Show the employee at this point in time,
        in ISO-8601 format.

    :>json string name: Human-readable name.
    :>json string uuid: Machine-friendly UUID.
    :>json object org: The organisation that this employee belongs to, as
        yielded by :http:get:`/service/o/`.
    :>json string cpr_no: CPR number of for the corresponding person.
        Please note that this is the only means for obtaining the CPR
        number; due to confidentiality requirements, all other end
        points omit it.

    :status 200: Whenever the user ID is valid and corresponds to an
        existing user.
    :status 404: Otherwise.

    **Example Response**:

    .. sourcecode:: json

      {
        "cpr_no": "1011101010",
        "name": "Hans Bruger",
        "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3",
        "org": {
          "name": "Magenta ApS",
          "user_key": "Magenta ApS",
          "uuid": "8efbd074-ad2a-4e6a-afec-1d0b1891f566"
        }
      }

    '''
    c = common.get_connector()

    r = get_one_employee(c, id, user=None, details=EmployeeDetails.FULL)

    if r:
        return flask.jsonify(r)
    else:
        exceptions.ErrorCodes.E_USER_NOT_FOUND()


@blueprint.route('/e/<uuid:employee_uuid>/terminate', methods=['POST'])
@util.restrictargs('force')
def terminate_employee(employee_uuid):
    """Terminates an employee and all of his roles beginning at a
    specified date. Except for the manager roles, which we vacate
    instead.

    .. :quickref: Employee; Terminate

    :query boolean force: When ``true``, bypass validations.

    :statuscode 200: The termination succeeded.

    :param employee_uuid: The UUID of the employee to be terminated.

    :<json string to: When the termination should occur, as an ISO 8601 date.
    :<json boolean terminate_all: *Optional* - perform full termination, i.e.
        terminate the associated manager functions as well.

    **Example Request**:

    .. sourcecode:: json

      {
        "validity": {
          "to": "2015-12-31"
        }
      }

    """
    request = flask.request.get_json()
    date = util.get_valid_to(request)

    validator.is_edit_from_date_before_today(date)

    c = lora.Connector(effective_date=date, virkningtil='infinity')

    request_handlers = [
        handlers.get_handler_for_function(obj)(
            {
                "type": handlers.get_key_for_function(obj),
                'uuid': objid,
                'original': obj,
                'indirect': not request.get('terminate_all'),
                'validity': {
                    'to': util.to_iso_date(
                        # we also want to handle _future_ relations
                        max(date, min(map(util.get_effect_from,
                                          util.get_states(obj)))),
                        is_end=True,
                    ),
                },
            },
            handlers.RequestType.TERMINATE,
        )
        for objid, obj in c.organisationfunktion.get_all(
            tilknyttedebrugere=employee_uuid,
            gyldighed='Aktiv',
        )
    ]

    for handler in request_handlers:
        handler.submit()

    # Write a noop entry to the user, to be used for the history
    common.add_history_entry(c.bruger, employee_uuid, "Afslut medarbejder")

    # TODO:
    return flask.jsonify(employee_uuid), 200


@blueprint.route('/e/<uuid:employee_uuid>/history/', methods=['GET'])
@util.restrictargs()
def get_employee_history(employee_uuid):
    """
    Get the history of an employee

    .. :quickref: Employee; Get history

    :param employee_uuid: The UUID of the employee

    **Example response**:

    :<jsonarr string from: When the change is active from
    :<jsonarr string to: When the change is active to
    :<jsonarr string action: The action performed
    :<jsonarr string life_cycle_code: The type of action performed
    :<jsonarr string user_ref: A reference to the user who made the change

    .. sourcecode:: json

      [
        {
          "from": "2018-02-21T11:27:20.909206+01:00",
          "to": "infinity",
          "action": "Opret orlov",
          "life_cycle_code": "Rettet",
          "user_ref": "42c432e8-9c4a-11e6-9f62-873cf34a735f"
        },
        {
          "from": "2018-02-21T11:27:20.803682+01:00",
          "to": "2018-02-21T11:27:20.909206+01:00",
          "action": "Rediger engagement",
          "life_cycle_code": "Rettet",
          "user_ref": "42c432e8-9c4a-11e6-9f62-873cf34a735f"
        },
        {
          "from": "2018-02-21T11:27:20.619990+01:00",
          "to": "2018-02-21T11:27:20.803682+01:00",
          "action": null,
          "life_cycle_code": "Importeret",
          "user_ref": "42c432e8-9c4a-11e6-9f62-873cf34a735f"
        }
      ]

    """

    c = lora.Connector()
    user_registrations = c.bruger.get(uuid=employee_uuid,
                                      registreretfra='-infinity',
                                      registrerettil='infinity')

    if not user_registrations:
        exceptions.ErrorCodes.E_USER_NOT_FOUND(employee_uuid=employee_uuid)

    history_entries = list(map(common.convert_reg_to_history,
                               user_registrations))

    return flask.jsonify(history_entries)


@blueprint.route('/e/create', methods=['POST'])
@util.restrictargs('force')
def create_employee():
    """Create a new employee

    .. :quickref: Employee; Create

    :query boolean force: When ``true``, bypass validations.

    :statuscode 200: Creation succeeded.

    **Example Request**:

    :<json string name: The name of the employee
    :<json string cpr_no: The CPR no of the employee
    :<json string user_key: Short, unique key identifying the employee.
    :<json object org: The organisation with which the employee is associated
    :<json string uuid: An **optional** parameter, that will be used as the
      UUID for the employee.
    :<json list details: A list of details to be created for the employee.

    For more information on the available details,
    see: :http:post:`/service/details/create`.
    Note, that the ``person`` parameter is implicit in these payload, and
    should not be given.

    .. sourcecode:: json

      {
        "name": "Name Name",
        "cpr_no": "0101501234",
        "user_key": "1234",
        "org": {
          "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
        "uuid": "f005a114-e5ef-484b-acfd-bff321b26e3f",
        "details": [
          {
            "type": "engagement",
            "org_unit": {
              "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
            },
            "job_function": {
              "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
            },
            "engagement_type": {
              "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
            },
            "validity": {
                "from": "2016-01-01",
                "to": "2017-12-31"
            }
          }
        ]
      }

    :returns: UUID of created employee

    """
    req = flask.request.get_json()
    request = EmployeeRequestHandler(req, handlers.RequestType.CREATE)
    return flask.jsonify(request.submit()), 201


def _inject_persons(details, employee_uuid, valid_from, valid_to):
    decorated = copy.deepcopy(details)
    for detail in decorated:
        detail['person'] = {
            mapping.UUID: employee_uuid,
            mapping.VALID_FROM: valid_from,
            mapping.VALID_TO: valid_to,
            'allow_nonexistent': True
        }

    return decorated

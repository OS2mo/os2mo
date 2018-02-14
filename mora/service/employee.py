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

'''

import flask

from mora import lora
from . import association, common, engagement, itsystem, org, keys, leave, role
from .. import util
from ..converters import writing

blueprint = flask.Blueprint('employee', __name__, static_url_path='',
                            url_prefix='/service')


def get_one_employee(c, userid, user=None, full=False):
    if not user:
        user = c.bruger.get(userid)

    props = user['attributter']['brugeregenskaber'][0]

    r = {
        keys.NAME: props['brugernavn'],
        keys.UUID: userid,
    }

    if full:
        rels = user['relationer']
        orgid = rels['tilhoerer'][0]['uuid']

        r[keys.CPR_NO] = (
            rels['tilknyttedepersoner'][0]['urn'].rsplit(':', 1)[-1]
        )
        r[keys.ORG] = org.get_one_organisation(c, orgid)

    return r


@blueprint.route('/o/<uuid:orgid>/e/')
@util.restrictargs('at', 'start', 'limit', 'query')
def list_employees(orgid):
    '''Query employees in an organisation.

    .. :quickref: Employee; List & search

    :param uuid orgid: UUID of the organisation to search.

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by employees matching this string.
        Please note that this only applies to attributes of the user, not the
        relations or engagements they have.

    :<jsonarr string name: Human-readable name.
    :<jsonarr string uuid: Machine-friendly UUID.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Hans Bruger",
          "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3"
        },
        {
          "name": "Joe User",
          "uuid": "cd2dcfad-6d34-4553-9fee-a7023139a9e8"
        }
      ]

    '''

    # TODO: share code with list_orgunits?

    c = common.get_connector()

    args = flask.request.args

    kwargs = dict(
        limit=int(args.get('limit', 0)) or 20,
        start=int(args.get('start', 0)) or 0,
        tilhoerer=str(orgid),

        # this makes the search go slow :(
        gyldighed='Aktiv',
    )

    if 'query' in args:
        kwargs.update(vilkaarligattr='%{}%'.format(args['query']))

    return flask.jsonify([
        get_one_employee(c, brugerid, bruger)
        for brugerid, bruger in c.bruger.get_all(**kwargs)
    ])


@blueprint.route('/e/<uuid:id>/')
@util.restrictargs('at')
def get_employee(id):
    '''Retrieve an employee.

    .. :quickref: Employee; Get

    :queryparam date at: Current time in ISO-8601 format.

    :<json string name: Human-readable name.
    :<json string uuid: Machine-friendly UUID.
    :<json object org: The organisation that this employee belongs to, as
        yielded by :http:get:`/service/o/`.
    :<json string cpr_no: CPR number of for the corresponding person.
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

    return flask.jsonify(get_one_employee(c, id, full=True))


@blueprint.route('/e/<uuid:employee_uuid>/create', methods=['POST'])
def create_employee(employee_uuid):
    """Creates new employee relations

    .. :quickref: Employee; Create

    :statuscode 200: Creation succeeded.

    :param employee_uuid: The UUID of the employee.

    All requests contain validity objects on the following form:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "from": "2016-01-01T00:00:00+00:00",
        "to": "2018-01-01T00:00:00+00:00",
      }

    Request payload contains a list of creation objects, each differentiated
    by the attribute 'type'. Each of these object types are detailed below:

    **Engagement**:

    :<jsonarr string type: **"engagement"**
    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string job_function: The job function of the association
    :<jsonarr string engagement_type: The engagement type
    :<jsonarr object validity: The validities of the created object.

    .. sourcecode:: json

      [
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
              "from": "2016-01-01T00:00:00+00:00",
              "to": "2018-01-01T00:00:00+00:00"
          }
        }
      ]

    **Association**:

    :<jsonarr string type: **"association"**
    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string job_function: The job function of the association
    :<jsonarr string association_type: The association type
    :<jsonarr string location: The associated location.
    :<jsonarr object validity: The validities of the created object.

    .. sourcecode:: json

      [
        {
          "type": "association",
          "org_unit": {
            "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
          },
          "job_function": {
            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
          },
          "association_type": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
          },
          "location": {
            "uuid": "89faa44c-f37a-4e4a-9cd8-b25f67cfd7bc"
          },
          "validity": {
              "from": "2016-01-01T00:00:00+00:00",
              "to": "2018-01-01T00:00:00+00:00"
          },
        }
      ]

    **IT system**:

    :<json string type: ``"it"``
    :<json object itsystem: The IT system to create a relation to, as
        returned by :http:get:`/o/(uuid:orgid)/it/`. The only
        mandatory field is ``uuid``.

    .. sourcecode:: json
      [
          {
              "type": "it",
              "itsystem": {
                  "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb"
              },
              "validity": {
                  "from": "2017-12-01T00:00:00+01",
                  "to": null
              }
          }
      ]

    **Role**:

    :<jsonarr string type: **"role"**
    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string role_type: The role type
    :<jsonarr object validity: The validities of the created object.

    .. sourcecode:: json

      [
        {
          "type": "role",
          "org_unit": {
            "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
          },
          "role_type": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
          },
          "validity": {
              "from": "2016-01-01T00:00:00+00:00",
              "to": "2018-01-01T00:00:00+00:00"
          }
        }
      ]

    **Leader**:

    **Leave**:

    :<jsonarr string type: **"leave"**
    :<jsonarr string leave_type: The leave type
    :<jsonarr object validity: The validities of the created object.

    .. sourcecode:: json

      [
        {
          "type": "leave",
          "leave_type": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
          },
          "validity": {
              "from": "2016-01-01T00:00:00+00:00",
              "to": "2018-01-01T00:00:00+00:00"
          },
        }
      ]

    """

    handlers = {
        'engagement': engagement.create_engagement,
        'association': association.create_association,
        'it': itsystem.create_system,
        'role': role.create_role,
        'contact': writing.create_contact,
        # 'leader': create_leader,
        'leave': leave.create_leave,
    }

    reqs = flask.request.get_json()
    for req in reqs:
        role_type = req.get('type')
        handler = handlers.get(role_type)

        if not handler:
            return flask.jsonify('Unknown role type: ' + role_type), 400

        handler(str(employee_uuid), req)

    # TODO:
    return flask.jsonify(employee_uuid), 200


@blueprint.route('/e/<uuid:employee_uuid>/edit', methods=['POST'])
def edit_employee(employee_uuid):
    """Edits an employee

    .. :quickref: Employee; Edit employee

    :statuscode 200: The edit succeeded.

    All requests contain validity objects on the following form:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "from": "2016-01-01T00:00:00+00:00",
        "to": "2018-01-01T00:00:00+00:00",
      }

    Request payload contains a list of edit objects, each differentiated
    by the attribute 'type'. Each of these object types are detailed below:

    **Engagement**:

    :param employee_uuid: The UUID of the employee.

    :<json string type: **"engagement"**
    :<json string uuid: The UUID of the engagement,
    :<json object original: An **optional** object containing the original
        state of the engagement to be overwritten. If supplied, the change
        will modify the existing registration on the engagement object.
        Detailed below.
    :<json object data: An object containing the changes to be made to the
        engagement. Detailed below.

    The **original** and **data** objects follow the same structure.
    Every field in **original** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string job_function: The job function of the association
    :<jsonarr string engagement_type: The engagement type
    :<jsonarr object validity: The validities of the changes.

    .. sourcecode:: json

      [
        {
          "type": "engagement",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
            "validity": {
              "from": "2016-01-01T00:00:00+00:00",
              "to": "2018-01-01T00:00:00+00:00"
            },
            "job_function": {
              "uuid": "5b56432c-f289-4d81-a328-b878ea0a4e1b"
            },
            "engagement_type": {
              "uuid": "743a6448-2b0b-48cf-8a2e-bf938a6181ee"
            },
            "org_unit": {
              "uuid": "04f73c63-1e01-4529-af2b-dee36f7c83cb"
            }
          },
          "data": {
            "validity": {
              "from": "2016-01-01T00:00:00+00:00",
              "to": "2019-01-01T00:00:00+00:00"
            },
            "job_function": {
              "uuid": "5b56432c-f289-4d81-a328-b878ea0a4e1b"
            }
          }
        }
      ]

    **Association**:

    :param employee_uuid: The UUID of the employee.

    :<json string type: **"association"**
    :<json string uuid: The UUID of the association,
    :<json object original: An **optional** object containing the original
        state of the association to be overwritten. If supplied, the change
        will modify the existing registration on the association object.
        Detailed below.
    :<json object data: An object containing the changes to be made to the
        association. Detailed below.

    The **original** and **data** objects follow the same structure.
    Every field in **original** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string job_function: The job function of the association
    :<jsonarr string association_type: The association type
    :<jsonarr string location: The associated location.
    :<jsonarr object validity: The validities of the changes.

    .. sourcecode:: json

      [
        {
          "type": "association",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
            "validity": {
                "from": "2016-01-01T00:00:00+00:00",
                "to": "2018-01-01T00:00:00+00:00"
            },
            "job_function": {
              "uuid": "5b56432c-f289-4d81-a328-b878ea0a4e1b"
            },
            "association_type": {
              "uuid": "743a6448-2b0b-48cf-8a2e-bf938a6181ee"
            },
            "org_unit": {
              "uuid": "04f73c63-1e01-4529-af2b-dee36f7c83cb"
            },
            "location": {
              "uuid": "89faa44c-f37a-4e4a-9cd8-b25f67cfd7bc"
            }
          },
          "data": {
            "validity": {
                "from": "2016-01-01T00:00:00+00:00",
                "to": "2019-01-01T00:00:00+00:00"
            },
            "job_function": {
              "uuid": "5b56432c-f289-4d81-a328-b878ea0a4e1b"
            }
          }
        }
      ]

    **IT system**:

    :param employee_uuid: The UUID of the employee.

    :<json string type: ``"it"``
    :<json string uuid: The UUID of the IT system,
    :<json object original: An **optional** object containing the original
        state of the role to be overwritten. If supplied, the change will
        modify the existing registration on the role object. Detailed below.
    :<json object data: An object containing the changes to be made to the
        role. Detailed below.

    The **original** and **data** objects follow the same structure.
    Every field in **original** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string uuid: Change the IT system to another.

    .. sourcecode:: json

    [
       {
         "type": "it",
         "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
         "original": {
             "name": "Active Directory",
             "user_name": "Fedtmule",
             "uuid": "00000000-0000-0000-0000-000000000000",
             "validity": {
                 "from": "2002-02-14T00:00:00+01:00",
                 "to": null
             },
         },
         "data": {
             "uuid": "11111111-1111-1111-1111-111111111111",
             "validity": {
                 "to": "2020-01-01T00:00:00+01:00"
             },
         },
     },

    **Role**:

    :param employee_uuid: The UUID of the employee.

    :<json string type: **"role"**
    :<json string uuid: The UUID of the role,
    :<json object original: An **optional** object containing the original
        state of the role to be overwritten. If supplied, the change will
        modify the existing registration on the role object. Detailed below.
    :<json object data: An object containing the changes to be made to the
        role. Detailed below.

    The **original** and **data** objects follow the same structure.
    Every field in **original** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string role_type: The role type
    :<jsonarr string location: The associated location.
    :<jsonarr object validity: The validities of the changes.

    .. sourcecode:: json

      [
        {
          "type": "role",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
            "validity": {
                "from": "2016-01-01T00:00:00+00:00",
                "to": "2018-01-01T00:00:00+00:00"
            },
            "role_type": {
              "uuid": "743a6448-2b0b-48cf-8a2e-bf938a6181ee"
            },
            "org_unit": {
              "uuid": "04f73c63-1e01-4529-af2b-dee36f7c83cb"
            }
          },
          "data": {
            "validity": {
                "from": "2016-01-01T00:00:00+00:00",
                "to": "2019-01-01T00:00:00+00:00"
            },
            "role_type": {
              "uuid": "eee27f47-8355-4ae2-b223-0ee0fdad81be"
            }
          }
        }
      ]

    **Leave**:

    :param employee_uuid: The UUID of the employee.

    :<json string type: **"leave"**
    :<json string uuid: The UUID of the leave,
    :<json object original: An **optional** object containing the original
        state of the leave to be overwritten. If supplied, the change will
        modify the existing registration on the leave object. Detailed below.
    :<json object data: An object containing the changes to be made to the
        leave. Detailed below.

    The **original** and **data** objects follow the same structure.
    Every field in **original** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string leave_type: The leave type
    :<jsonarr object validity: The validities of the changes.

    .. sourcecode:: json

      [
        {
          "type": "leave",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
            "validity": {
                "from": "2016-01-01T00:00:00+00:00",
                "to": "2018-01-01T00:00:00+00:00"
            },
            "leave_type": {
              "uuid": "743a6448-2b0b-48cf-8a2e-bf938a6181ee"
            }
          },
          "data": {
            "validity": {
                "from": "2016-01-01T00:00:00+00:00",
                "to": "2019-01-01T00:00:00+00:00"
            },
            "leave_type": {
              "uuid": "eee27f47-8355-4ae2-b223-0ee0fdad81be"
            }
          }
        }
      ]
    """

    handlers = {
        'engagement': engagement.edit_engagement,
        'association': association.edit_association,
        'role': role.edit_role,
        'it': itsystem.edit_system,
        'leave': leave.edit_leave,
        # 'contact': edit_contact,
        # 'leader': edit_leader,
    }

    reqs = flask.request.get_json()

    # TODO: pre-validate all requests, since we should either handle
    # all or none of them
    for req in reqs:
        role_type = req.get('type')
        handler = handlers.get(role_type)

        if not handler:
            return flask.jsonify('Unknown role type: ' + role_type), 400

        handler(str(employee_uuid), req)

    # TODO: Figure out the response -- probably just the edited object(s)?
    return flask.jsonify(employee_uuid), 200


@blueprint.route('/e/<uuid:employee_uuid>/terminate', methods=['POST'])
def terminate_employee(employee_uuid):
    """Terminates an employee and all of his roles from a specified date.

    .. :quickref: Employee; Terminate

    :statuscode 200: The termination succeeded.

    :param employee_uuid: The UUID of the employee to be terminated.

    :<json string valid_from: The date on which the termination should happen,
                              in ISO 8601.

    **Example Request**:

    .. sourcecode:: json

      {
        "valid_from": "2016-01-01T00:00:00+00:00"
      }
    """
    date = flask.request.get_json().get(keys.VALID_FROM)

    c = lora.Connector(effective_date=date)

    # Org funks
    types = (
        keys.ENGAGEMENT_KEY,
        keys.ASSOCIATION_KEY,
        keys.ROLE_KEY,
        keys.LEAVE_KEY,
    )
    for key in types:
        for obj in c.organisationfunktion.get_all(
            tilknyttedebrugere=employee_uuid,
            funktionsnavn=key
        ):
            c.organisationfunktion.update(
                common.inactivate_org_funktion_payload(
                    date,
                    "Afslut medarbejder"),
                obj[0])

    # TODO:
    return flask.jsonify(employee_uuid), 200

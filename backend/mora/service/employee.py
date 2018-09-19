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

import uuid

import flask

from .. import mapping
from .. import exceptions
from . import address
from . import association
from .. import common
from . import engagement
from . import itsystem
from . import manager
from . import leave
from . import org
from . import role
from .. import lora
from .. import settings
from .. import util

blueprint = flask.Blueprint('employee', __name__, static_url_path='',
                            url_prefix='/service')


RELATION_TYPES = {
    'address': address.Addresses,
}


def get_one_employee(c, userid, user=None, full=False):
    if not user:
        user = c.bruger.get(userid)

        if not user or not util.is_reg_valid(user):
            return None

    props = user['attributter']['brugeregenskaber'][0]

    r = {
        mapping.NAME: props['brugernavn'],
        mapping.UUID: userid,
    }

    if full:
        rels = user['relationer']
        orgid = rels['tilhoerer'][0]['uuid']

        if rels.get('tilknyttedepersoner'):
            r[mapping.CPR_NO] = (
                rels['tilknyttedepersoner'][0]['urn'].rsplit(':', 1)[-1]
            )

        r[mapping.ORG] = org.get_one_organisation(c, orgid)
        r[mapping.USER_KEY] = props['brugervendtnoegle']

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
        tilhoerer=str(orgid),
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

    r = get_one_employee(c, id, full=True)

    if r:
        return flask.jsonify(r)
    else:
        raise exceptions.HTTPException(exceptions.ErrorCodes.E_USER_NOT_FOUND)


@blueprint.route('/e/<uuid:employee_uuid>/create', methods=['POST'])
def create_employee_relation(employee_uuid):
    """Creates new employee relations

    .. :quickref: Employee; Create relation

    :statuscode 200: Creation succeeded.

    :param employee_uuid: The UUID of the employee.

    All requests contain validity objects on the following form:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "from": "2016-01-01",
        "to": "2017-12-31",
      }

    Request payload contains a list of creation objects, each differentiated
    by the attribute ``type``. Each of these object types are detailed below:

    **Engagement**:

    :<jsonarr string type: **"engagement"**
    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string job_function: The job function of the association
    :<jsonarr string engagement_type: The engagement type
    :<jsonarr object validity: The validities of the created object.

    The parameters ``job_function`` and ``engagement_type`` should contain
    UUIDs obtained from their respective facet endpoints.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.

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
              "from": "2016-01-01",
              "to": "2017-12-31"
          }
        }
      ]

    **Association**:

    :<jsonarr string type: **"association"**
    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string job_function: The job function of the association
    :<jsonarr string association_type: The association type
    :<jsonarr string address: The associated address.
    :<jsonarr object validity: The validities of the created object.

    The parameters ``job_function`` and ``association_type`` should contain
    UUIDs obtained from their respective facet endpoints.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    For the ``address`` parameter, see :ref:`Adresses <address>`.

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
          "address": {
            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
            "address_type": {
              "example": "<UUID>",
              "name": "Adresse",
              "scope": "DAR",
              "user_key": "Adresse",
              "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
            }
          },
          "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
          }
        }
      ]

    **IT system**:

    :<json string type: ``"it"``
    :<json string user_key: The account name on the IT system.
    :<json object itsystem: The IT system to create a relation to, as
        returned by :http:get:`/service/o/(uuid:orgid)/it/`.

    .. sourcecode:: json

      [
        {
          "type": "it",
          "user_key": "goofy-moofy",
          "itsystem": {
             "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697"
          },
          "validity": {
            "from": "2018-09-01",
             "to": null
          }
        }
      ]

    **Role**:

    :<jsonarr string type: **"role"**
    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string role_type: The role type
    :<jsonarr object validity: The validities of the created object.

    The parameter ``role_type`` should contain a UUID obtained from the
    respective facet endpoint.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.

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
              "from": "2016-01-01",
              "to": "2017-12-31"
          }
        }
      ]

    **Manager**:

    :<jsonarr string type: **"manager"**
    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string manager_type: The manager type
    :<jsonarr array responsibility: The manager responsibilities
    :<jsonarr string manager_level: The manager level
    :<jsonarr string address: The associated address.
    :<jsonarr object validity: The validities of the created object.

    The parameters ``manager_type``, ``responsibility`` and ``manager_level``
    should contain UUIDs obtained from their respective facet endpoints.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    For the ``address`` parameter, see :ref:`Adresses <address>`.

    It is also possible to create a vacant manager position. To do this, use
    the ou/ endpoint to create the manager.

    .. sourcecode:: json

      [
        {
          "type": "manager",
          "org_unit": {
            "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
          },
          "manager_type": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
          },
          "responsibility": [
            {
              "uuid": "e6b24f90-b056-433b-ad65-e6ab95d25826"
            }
          ],
          "manager_level": {
            "uuid": "f17f2d60-9750-4577-a367-8a5f065b63fa"
          },
          "address": {
            "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
            "address_type": {
              "example": "<UUID>",
              "name": "Adresse",
              "scope": "DAR",
              "user_key": "Adresse",
              "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
            }
          },
          "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
          }
        }
      ]

    **Leave**:

    :<jsonarr string type: **"leave"**
    :<jsonarr string leave_type: The leave type
    :<jsonarr object validity: The validities of the created object.

    The parameter ``leave_type`` should contain a UUID obtained from the
    respective facet endpoint.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.

    .. sourcecode:: json

      [
        {
          "type": "leave",
          "leave_type": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
          },
          "validity": {
              "from": "2016-01-01",
              "to": "2017-12-31"
          },
        }
      ]

    **Address**:

    :<jsonarr string type: ``"address"``
    :<jsonarr object address_type: The type of the address, exactly as
        returned by returned by
        :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr string value: The value of the address field. Please
        note that as a special case, this should be a UUID for *DAR*
        addresses.
    :<jsonarr object validity: The validities of the created object.

    See :ref:`Adresses <address>` for more information.

    .. sourcecode:: json

      [
        {
          "value": "0101501234",
          "address_type": {
            "example": "5712345000014",
            "name": "EAN",
            "scope": "EAN",
            "user_key": "EAN",
            "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"
          },
          "type": "address",
          "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
          }
        }
      ]

    """

    handlers = {
        'engagement': engagement.create_engagement,
        'association': association.create_association,
        'role': role.create_role,
        'manager': manager.create_manager,
        'leave': leave.create_leave,
        'it': itsystem.create_itsystem,
        **RELATION_TYPES,
    }

    reqs = flask.request.get_json()
    for req in reqs:
        role_type = req.get('type')
        handler = handlers.get(role_type)

        if not handler:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_UNKNOWN_ROLE_TYPE,
                message=role_type)

        elif issubclass(handler, common.AbstractRelationDetail):
            handler(common.get_connector().bruger).create(
                str(employee_uuid),
                req,
            )

        else:
            handler(str(employee_uuid), req)

        # Write a noop entry to the user, to be used for the history
        common.add_bruger_history_entry(
            employee_uuid,
            "Opret {}".format(mapping.RELATION_TRANSLATIONS[role_type])
        )

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
        "from": "2016-01-01",
        "to": "2017-12-31"
      }

    Request payload contains a list of edit objects, each differentiated
    by the attribute ``type``. Each of these object types are detailed below:

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

    The parameters ``job_function`` and ``engagement_type`` should contain
    UUIDs obtained from their respective facet endpoints.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.

    .. sourcecode:: json

      [
        {
          "type": "engagement",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
            "validity": {
              "from": "2016-01-01",
              "to": "2017-12-31"
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
              "from": "2016-01-01",
              "to": "2018-12-31"
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
    :<jsonarr string address: The associated address object.
    :<jsonarr object validity: The validities of the changes.

    The parameters ``job_function`` and ``association_type`` should contain
    UUIDs obtained from their respective facet endpoints.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    For the ``address`` parameter, see :ref:`Adresses <address>`.

    .. sourcecode:: json

      [
        {
          "type": "association",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
            "validity": {
                "from": "2016-01-01",
                "to": "2016-12-31"
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
            "address": {
              "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
              "address_type": {
                "example": "<UUID>",
                "name": "Adresse",
                "scope": "DAR",
                "user_key": "Adresse",
                "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
              }
            }
          },
          "data": {
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31"
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
    :<json string uuid: The UUID of the IT system responsibility"
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
                "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
                "original": {
                    "itsystem": {
                        "name": "Active Directory",
                        "reference": null,
                        "system_type": null,
                        "user_key": "AD",
                        "uuid": "59c135c9-2b15-41cc-97c8-b5dff7180beb",
                        "validity": {
                            "from": "2002-02-14",
                            "to": null,
                        }
                    },
                    "org_unit": null,
                    "person": {
                        "name": "Anders And",
                        "uuid": "53181ed2-f1de-4c4a-a8fd-ab358c2c454a",
                    },
                    "user_key": "donald",
                    "uuid": "aaa8c495-d7d4-4af1-b33a-f4cb27b82c66",
                    "validity": {
                        "from": "2017-01-01",
                        "to": null,
                    }
                },
                "data": {
                    "itsystem": {
                        "uuid": "0872fb72-926d-4c5c-a063-ff800b8ee697",
                    },
                    "user_key": "donald_duck"
                    "validity": {
                        "from": "2017-06-01",
                        "to": "2018-06-01"
                    }
                }
            }
        ]

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
    :<jsonarr object validity: The validities of the changes.

    The parameter ``role_type`` should contain a UUID obtained from the
    respective facet endpoint.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.

    .. sourcecode:: json

      [
        {
          "type": "role",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
            "validity": {
                "from": "2016-01-01",
                "to": "2017-12-31"
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
                "from": "2016-01-01",
                "to": "2018-12-31"
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

    The parameter ``leave_type`` should contain a UUID obtained from the
    respective facet endpoint.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.

    .. sourcecode:: json

      [
        {
          "type": "leave",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
            "validity": {
                "from": "2016-01-01",
                "to": "2017-12-31"
            },
            "leave_type": {
              "uuid": "743a6448-2b0b-48cf-8a2e-bf938a6181ee"
            }
          },
          "data": {
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31"
            },
            "leave_type": {
              "uuid": "eee27f47-8355-4ae2-b223-0ee0fdad81be"
            }
          }
        }
      ]

    **Manager**:

    :param employee_uuid: The UUID of the employee.

    :<json string type: **"manager"**
    :<json string uuid: The UUID of the manager,
    :<json object original: An **optional** object containing the original
        state of the leave to be overwritten. If supplied, the change will
        modify the existing registration on the leave object. Detailed below.
    :<json object data: An object containing the changes to be made to the
        leave. Detailed below.

    The **original** and **data** objects follow the same structure.
    Every field in **original** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string manager_type: The manager type
    :<jsonarr string org_unit: The associated org unit
    :<jsonarr string manager_type: The manager type
    :<jsonarr array responsibilities: The manager responsibilities
    :<jsonarr string manager_level: The manager level
    :<jsonarr string address: The associated address object.
    :<jsonarr object validity: The validities of the changes.

    The parameters ``manager_type``, ``responsibility`` and ``manager_level``
    should contain UUIDs obtained from their respective facet endpoints.
    See :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    For the ``address`` parameter, see :ref:`Adresses <address>`.

    .. sourcecode:: json

      [
        {
          "type": "manager",
          "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
          "original": {
              "org_unit": {
                "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
              },
              "manager_type": {
                "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
              },
              "responsibility": [
                {
                  "uuid": "e6b24f90-b056-433b-ad65-e6ab95d25826"
                }
              ],
              "manager_level": {
                "uuid": "f17f2d60-9750-4577-a367-8a5f065b63fa"
              },
              "address": {
                "uuid": "b1f1817d-5f02-4331-b8b3-97330a5d3197",
                "address_type": {
                  "example": "<UUID>",
                  "name": "Adresse",
                  "scope": "DAR",
                  "user_key": "Adresse",
                  "uuid": "4e337d8e-1fd2-4449-8110-e0c8a22958ed"
                }
              },
              "validity": {
                  "from": "2016-01-01",
                  "to": "2017-12-31"
              }
          },
          "data": {
            "validity": {
                "from": "2016-01-01",
                "to": "2018-12-31"
            },
            "manager_type": {
              "uuid": "eee27f47-8355-4ae2-b223-0ee0fdad81be"
            }
          }
        }
      ]

    **Address**:

    :<jsonarr string type: ``"address"``
    :<jsonarr object address_type: The type of the address, exactly as
        returned by returned by
        :http:get:`/service/o/(uuid:orgid)/f/(facet)/`.
    :<jsonarr string value: The value of the address field. Please
        note that as a special case, this should be a UUID for *DAR*
        addresses.
    :<jsonarr object validity: A validity object

    See :ref:`Adresses <address>` for more information.

    .. sourcecode:: json

      [
        {
          "original": {
            "value": "0101501234",
            "address_type": {
              "example": "5712345000014",
              "name": "EAN",
              "scope": "EAN",
              "user_key": "EAN",
              "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"
            },
          },
          "data": {
            "value": "123456789",
            "address_type": {
              "example": "5712345000014",
              "name": "EAN",
              "scope": "EAN",
              "user_key": "EAN",
              "uuid": "e34d4426-9845-4c72-b31e-709be85d6fa2"
            },
          },
          "type": "address",
          "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
          }
        }
      ]
    """

    handlers = {
        'engagement': engagement.edit_engagement,
        'association': association.edit_association,
        'role': role.edit_role,
        'leave': leave.edit_leave,
        'manager': manager.edit_manager,
        'it': itsystem.edit_itsystem,
        **RELATION_TYPES,
    }

    reqs = flask.request.get_json()

    # TODO: pre-validate all requests, since we should either handle
    # all or none of them
    for req in reqs:
        role_type = req.get('type')
        handler = handlers.get(role_type)

        if not handler:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_UNKNOWN_ROLE_TYPE,
                message=role_type)

        elif issubclass(handler, common.AbstractRelationDetail):
            handler(common.get_connector().bruger).edit(
                str(employee_uuid),
                req,
            )

        else:
            handler(str(employee_uuid), req)

        # Write a noop entry to the user, to be used for the history
        common.add_bruger_history_entry(
            employee_uuid,
            "Rediger {}".format(mapping.RELATION_TRANSLATIONS[role_type])
        )

    # TODO: Figure out the response -- probably just the edited object(s)?
    return flask.jsonify(employee_uuid), 200


@blueprint.route('/e/<uuid:employee_uuid>/terminate', methods=['POST'])
def terminate_employee(employee_uuid):
    """Terminates an employee and all of his roles beginning at a
    specified date.

    .. :quickref: Employee; Terminate

    :statuscode 200: The termination succeeded.

    :param employee_uuid: The UUID of the employee to be terminated.

    :<json string to: When the termination should occur, as an ISO 8601 date.

    **Example Request**:

    .. sourcecode:: json

      {
        "validity": {
          "to": "2015-12-31"
        }
      }

    """
    date = util.get_valid_to(flask.request.get_json())

    # Org funks
    types = (
        mapping.ENGAGEMENT_KEY,
        mapping.ASSOCIATION_KEY,
        mapping.ROLE_KEY,
        mapping.LEAVE_KEY,
        mapping.MANAGER_KEY
    )

    c = lora.Connector(effective_date=date)

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

    # Write a noop entry to the user, to be used for the history
    common.add_bruger_history_entry(employee_uuid, "Afslut medarbejder")

    # TODO:
    return flask.jsonify(employee_uuid), 200


@blueprint.route('/e/<uuid:employee_uuid>/history/', methods=['GET'])
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
        raise exceptions.HTTPException(exceptions.ErrorCodes.E_USER_NOT_FOUND)

    history_entries = list(map(common.convert_reg_to_history,
                               user_registrations))

    return flask.jsonify(history_entries)


@blueprint.route('/e/create', methods=['POST'])
def create_employee():
    """Create a new employee

    .. :quickref: Employee; Create

    :statuscode 200: Creation succeeded.

    **Example Request**:

    :<json string name: The name of the employee
    :<json string cpr_no: The CPR no of the employee
    :<json string user_key: Short, unique key identifying the employee.
    :<json object org: The organisation with which the employee is associated
    :<json string uuid: An **optional** parameter, that will be used as the
      UUID for the employee.

    .. sourcecode:: json

      {
        "name": "Name Name",
        "cpr_no": "0101501234",
        "user_key": "1234",
        "org": {
          "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
        "uuid": "f005a114-e5ef-484b-acfd-bff321b26e3f"
      }

    :returns: UUID of created employee

    """

    c = lora.Connector()

    req = flask.request.get_json()

    name = util.checked_get(req, mapping.NAME, "", required=True)
    org_uuid = util.get_mapping_uuid(req, mapping.ORG, required=True)
    cpr = util.checked_get(req, mapping.CPR_NO, "", required=False)
    userid = util.get_uuid(req, required=False)

    try:
        valid_from = \
            util.get_cpr_birthdate(cpr) if cpr else util.NEGATIVE_INFINITY
    except ValueError as exc:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_CPR_NOT_VALID,
            cpr=cpr,
            cause=exc,
        )

    userids = c.bruger.fetch(
        tilknyttedepersoner="urn:dk:cpr:person:{}".format(cpr),
        tilhoerer=org_uuid
    )

    if userids and userid not in userids:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_EXISTING_CPR,
            cpr=cpr,
        )

    valid_to = util.POSITIVE_INFINITY

    # TODO: put something useful into the default user key
    bvn = util.checked_get(req, mapping.USER_KEY, str(uuid.uuid4()))

    user = common.create_bruger_payload(
        valid_from=valid_from,
        valid_to=valid_to,
        brugernavn=name,
        brugervendtnoegle=bvn,
        tilhoerer=org_uuid,
        cpr=cpr,
    )

    userid = c.bruger.create(user, uuid=userid)

    return flask.jsonify(userid)

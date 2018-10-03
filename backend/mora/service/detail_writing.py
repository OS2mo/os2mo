#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''
Writing details
---------------

This section describes how to write details to employees.

For more information regarding reading relations, refer to:

* :http:get:`/service/(any:type)/(uuid:id)/details/`

'''

import typing

import flask

from . import address
from . import association
from . import engagement
from . import itsystem
from . import leave
from . import manager
from . import orgunit
from . import role
from .. import exceptions

blueprint = flask.Blueprint('detail_writing', __name__, static_url_path='',
                            url_prefix='/service')


CREATION_HANDLERS = {
    'engagement': engagement.create_engagement,
    'association': association.create_association,
    'role': role.create_role,
    'manager': manager.create_manager,
    'leave': leave.create_leave,
    'it': itsystem.create_itsystem,
    'address': address.create_address
}

EDIT_HANDLERS = {
    'engagement': engagement.edit_engagement,
    'association': association.edit_association,
    'role': role.edit_role,
    'leave': leave.edit_leave,
    'manager': manager.edit_manager,
    'it': itsystem.edit_itsystem,
    'address': address.edit_address,
    'org_unit': orgunit.edit_orgunit,
}


def process_requests(handlers, reqs) -> typing.List[str]:
    if isinstance(reqs, dict):
        just_one = True
        reqs = [reqs]
    elif isinstance(reqs, list):
        just_one = False
    else:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_INVALID_INPUT,
            request=reqs,
        )

    operations = {req.get('type') for req in reqs}

    if not operations.issubset(handlers):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_UNKNOWN_ROLE_TYPE,
            types=sorted(operations - handlers.keys()),
        )

    r = [
        handlers[req.get('type')](req)
        for req in reqs
    ]

    if just_one:
        return r[0]
    else:
        return r


@blueprint.route('/details/create', methods=['POST'])
def create():
    """Creates new relations on employees and units

    .. :quickref: Writing; Create relation

    :statuscode 200: Creation succeeded.

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
    :<jsonarr object org_unit: The associated org unit
    :<jsonarr object person: The associated employee
    :<jsonarr object job_function: The job function of the association
    :<jsonarr object engagement_type: The engagement type
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
    :<jsonarr object org_unit: The associated org unit
    :<jsonarr object person: The associated employee
    :<jsonarr object job_function: The job function of the association
    :<jsonarr object association_type: The association type
    :<jsonarr object address: The associated address.
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
    :<json object org_unit: the UUID of the associated unit, if any
    :<json object person: the UUID of the associated employee, if any

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
    :<jsonarr object org_unit: The associated org unit
    :<jsonarr object person: The associated employee
    :<jsonarr object role_type: The role type
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
    :<jsonarr object org_unit: The associated org unit
    :<jsonarr object person: The associated employee, if applicable
    :<jsonarr object manager_type: The manager type
    :<jsonarr array responsibility: The manager responsibilities
    :<jsonarr object manager_level: The manager level
    :<jsonarr array address: The associated address.
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
    :<jsonarr object leave_type: The leave type
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

    return (
        flask.jsonify(
            process_requests(CREATION_HANDLERS,
                             flask.request.get_json()),
        ),
        201,
    )


@blueprint.route('/details/edit', methods=['POST'])
def edit():
    """Edits a relation or attribute on an employee or unit

    .. :quickref: Writing; Edit employee

    :param type: 'ou' for writing to a unit; 'e' for writing an
        employee.
    :param uuid uuid: The UUID to of the target of the operation, i.e. the ID
        of the employee or unit.

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
    :<jsonarr object job_function: The job function of the association
    :<jsonarr object engagement_type: The engagement type
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
    :<jsonarr object job_function: The job function of the association
    :<jsonarr object association_type: The association type
    :<jsonarr object address: The associated address object.
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

    :<json string type: ``"it"``
    :<json string uuid: The UUID of the role or relation
    :<json object original: An **optional** object containing the original
        state of the role to be overwritten. If supplied, the change will
        modify the existing registration on the role object. Detailed below.
    :<json object data: An object containing the changes to be made to the
        role. Detailed below.

    The **original** and **data** objects follow the same structure.
    Every field in **original** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<json string user_key: The account name on the IT system.
    :<json object itsystem: the UUID of the associated IT system
    :<json object org_unit: the UUID of the associated unit, if any
    :<json object person: the UUID of the associated employee, if any

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

    :<jsonarr object org_unit: The associated org unit
    :<jsonarr object person: The associated employee
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

    :<jsonarr object leave_type: The leave type
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

    :<jsonarr object manager_type: The manager type
    :<jsonarr object org_unit: The associated org unit
    :<jsonarr object person: The associated employee, if applicable
    :<jsonarr object manager_type: The manager type
    :<jsonarr array responsibilities: The manager responsibilities
    :<jsonarr object manager_level: The manager level
    :<jsonarr object address: The associated address object.
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
    :<jsonarr object value: The value of the address field. Please
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

    return (
        flask.jsonify(
            process_requests(EDIT_HANDLERS,
                             flask.request.get_json()),
        ),
        200,
    )

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastapi import APIRouter
from fastapi import Body

from ... import exceptions
from ... import lora
from ... import mapping
from ... import util
from .. import facet
from ..address_handler import base
from . import validator

_router = APIRouter()


@_router.post("/org-unit/", responses={"400": {"description": "Missing org unit"}})
async def org_unit_validity(req: dict = Body(...)):
    """
    Verify that an org unit is valid within a given set of start/end dates

    .. :quickref: Validate; Validate org unit

    :statuscode 200: Validation succeeded.
    :statuscode 400: Validation failed.

    :<json object org_unit: The associated org unit
    :<json object validity: The relevant validities to be checked

    .. sourcecode:: json

      {
        "org_unit": {
          "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
        },
        "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
        }
      }

    Possible validation errors:

    * ``V_INVALID_ADDRESS_DAR``
    * ``V_INVALID_ADDRESS_EAN``
    * ``V_INVALID_ADDRESS_EMAIL``
    * ``V_INVALID_ADDRESS_PNUMBER``
    * ``V_INVALID_ADDRESS_PHONE``
    * ``V_INVALID_ADDRESS_WWW``

    """
    org_unit = util.checked_get(req, mapping.ORG_UNIT, {}, required=True)
    valid_from, valid_to = util.get_validities(req)

    await validator.is_date_range_in_org_unit_range(org_unit, valid_from, valid_to)

    return {"success": True}


@_router.post("/employee/", responses={"400": {"description": "Missing employee"}})
async def employee_validity(req: dict = Body(...)):
    """
    Verify that an employee is valid within a given set of start/end dates

    .. :quickref: Validate; Validate employee

    :statuscode 200: Validation succeeded.
    :statuscode 400: Validation failed.

    :<json object org_unit: The associated org unit
    :<json object validity: The relevant validities to be checked

    .. sourcecode:: json

      {
        "person": {
          "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
        },
        "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
        }
      }

    Possible validation errors:

    * ``V_DATE_OUTSIDE_EMPL_RANGE``

    """
    employee = util.checked_get(req, mapping.PERSON, {}, required=True)
    valid_from, valid_to = util.get_validities(req)

    await validator.is_date_range_in_employee_range(employee, valid_from, valid_to)

    return {"success": True}


@_router.post("/cpr/", responses={"400": {"description": "Missing CPR number"}})
async def check_cpr(req: dict = Body(...)):
    """
    Verify that an employee with the given CPR no. does not already exist

    .. :quickref: Validate; Validate CPR no.

    :statuscode 200: Validation succeeded.
    :statuscode 400: Validation failed.

    :<json string cpr: The associated CPR number
    :<json object org: The associated organisation

    .. sourcecode:: json

      {
        "cpr_no": "1212121212",
        "org": {
          "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
        }
      }

    Possible validation errors:

    * ``V_EXISTING_CPR``
    """
    cpr = util.checked_get(req, mapping.CPR_NO, "", required=True)
    org_uuid = util.get_mapping_uuid(req, mapping.ORG, required=True)

    if await validator.does_employee_with_cpr_already_exist(
        cpr, util.NEGATIVE_INFINITY, util.POSITIVE_INFINITY, org_uuid
    ):
        raise exceptions.HTTPException(exceptions.ErrorCodes.V_EXISTING_CPR)
    # coverage: pause
    return {"success": True}
    # coverage: unpause


@_router.post(
    "/active-engagements/", responses={"400": {"description": "Missing person"}}
)
async def employee_engagements(req: dict = Body(...)):
    """
    Verify that an employee has active engagements

    .. :quickref: Validate; Validate active engagements

    :statuscode 200: Validation succeeded.
    :statuscode 400: Validation failed.

    :<json object person: The associated employee
    :<json object validity: The relevant validities to be checked

    .. sourcecode:: json

      {
        "person": {
          "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
        },
        "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
        }
      }

    Possible validation errors:

    * ``V_NO_ACTIVE_ENGAGEMENT``
    """
    employee_uuid = util.get_mapping_uuid(req, mapping.PERSON, required=True)
    valid_from, valid_to = util.get_validities(req)

    await validator.does_employee_have_active_engagement(
        employee_uuid, valid_from, valid_to
    )

    return {"success": True}


@_router.post(
    "/existing-associations/", responses={"400": {"description": "Missing person"}}
)
async def employee_existing_associations(req: dict = Body(...)):
    """
    Verify that an employee does not have existing associations for a given
    org unit

    .. :quickref: Validate; Validate existing associations

    :statuscode 200: Validation succeeded.
    :statuscode 400: Validation failed.

    :<json object person: The associated employee
    :<json object person: The associated org unit
    :<json object validity: The relevant validities to be checked
    :<json object uuid: The UUID of an existing association to be exempt
        from validation

    .. sourcecode:: json

      {
        "person": {
          "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
        },
        "org_unit": {
          "uuid": "c55e9eb3-2b23-4364-b5e4-dff51ddf289e"
        },
        "validity": {
            "from": "2016-01-01",
            "to": "2017-12-31"
        },
        "uuid": "df995126-e747-4f9f-8e3b-ca38cadbfdb1",
      }

    Possible validation errors:

    * ``V_MORE_THAN_ONE_ASSOCIATION``
    """
    employee_uuid = util.get_mapping_uuid(req, mapping.PERSON, required=True)
    org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT, required=True)
    association_uuid = util.get_uuid(req, required=False)
    valid_from = util.get_valid_from(req)

    await validator.does_employee_have_existing_association(
        employee_uuid, org_unit_uuid, valid_from, association_uuid
    )

    return {"success": True}


@_router.post(
    "/candidate-parent-org-unit/",
    responses={"400": {"description": "Missing org unit"}},
)
async def candidate_parent_org_unit(req: dict = Body(...)):
    """
    Verify that a given parent is a suitable candidate for an org unit move,
    i.e. that the candidate parent is not in the sub tree of the org unit being
    moved, and that the org unit being moved is not a root unit.

    .. :quickref: Validate; Validate candidate parent org unit

    :statuscode 200: Validation succeeded.
    :statuscode 400: Validation failed.

    :<json object org_unit: The associated org unit to be moved
    :<json object parent: The associated parent org unit
    :<json object from: The date on which the move is to take place

    .. sourcecode:: json

      {
        "org_unit": {
          "uuid": "c55e9eb3-2b23-4364-b5e4-dff51ddf289e"
        },
        "parent": {
          "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
        },
        "validity": {
            "from": "2016-01-01",
        }
      }

    Possible validation errors:

    * ``V_CANNOT_MOVE_UNIT_TO_ROOT_LEVEL``
    * ``V_ORG_UNIT_MOVE_TO_CHILD``
    * ``V_DATE_OUTSIDE_ORG_UNIT_RANGE``
    * ``V_UNIT_OUTSIDE_ORG``
    """
    org_unit_uuid = util.get_mapping_uuid(req, mapping.ORG_UNIT, required=True)
    parent_uuid = util.get_mapping_uuid(req, mapping.PARENT, required=True)
    valid_from = util.get_valid_from(req)

    await validator.is_candidate_parent_valid(org_unit_uuid, parent_uuid, valid_from)

    return {"success": True}


@_router.post("/address/")
async def address_value(req: dict = Body(...), only_primary_uuid: bool | None = None):
    """
    Verify that a given address value conforms to the format for the given
    address type. E.g. that a phone number consists of 8 digits.

    .. :quickref: Validate; Validate address value

    :statuscode 200: Validation succeeded.
    :statuscode 400: Validation failed.

    :<json object value: The address value to be checked
    :<json object address_type: The address type to be checked against

    .. sourcecode:: json

      {
        "value": "12345678",
        "address_type": {
          "uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec"
        }
      }

    Possible validation errors:

    * ``V_CANNOT_MOVE_UNIT_TO_ROOT_LEVEL``
    """

    address_type_uuid = util.get_mapping_uuid(req, mapping.ADDRESS_TYPE, required=True)
    value = util.checked_get(req, mapping.VALUE, default="", required=True)

    c = lora.Connector()

    type_obj = await facet.get_one_class(
        c, address_type_uuid, only_primary_uuid=only_primary_uuid
    )

    scope = util.checked_get(type_obj, "scope", "", required=True)

    handler = base.get_handler_for_scope(scope)
    await handler.validate_value(value)

    return {"success": True}


# important to include AFTER path_operations are in place
router = APIRouter()
router.include_router(_router, prefix="/validate")

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

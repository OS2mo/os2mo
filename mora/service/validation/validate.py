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

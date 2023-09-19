# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Facets
------

This sections describes how to interact with facets, i.e. the types of
objects.

    .. http:>jsonarr string name:: Human-readable name.
    .. http:>jsonarr string uuid:: Machine-friendly UUID.
    .. http:>jsonarr string user_key:: Short, unique key.
    .. http:>jsonarr string example:: An example value for the address field.
        A value of `<UUID>` means that this is a `DAR`_ address UUID.

"""
import logging
from asyncio import create_task
from asyncio import gather
from typing import Any
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter
from more_itertools import one

from . import handlers
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..exceptions import ErrorCodes
from ..lora import LoraObjectType
from mora.request_scoped.bulking import request_wide_bulk
from mora.service import clazz
from ramodels.mo.class_ import ClassWrite

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_one_facet(c, facetid, orgid=None, facet=None, data=None, validity=None):
    """Fetch a facet and enrich it."""

    # Use given facet or fetch one, if none is given
    facet = facet or (await c.facet.get(facetid))
    if facet is None:
        return None

    properties = facet["attributter"]["facetegenskaber"][0]
    bvn = properties.get("brugervendtnoegle", "")
    description = properties.get("beskrivelse", "")
    response = {
        "uuid": facetid,
        "user_key": bvn,
        "description": description,
    }

    if orgid:
        response["path"] = bvn and router.url_path_for(
            "get_classes", orgid=orgid, facet=bvn
        )

    if data:
        response["data"] = data

    return response


async def get_facet_from_cache(facetid, orgid=None, data=None) -> Any:
    """
    Get org unit from cache and process it
    :param facetid: uuid of facet
    :param facet:
    :param data:
    :return: A processed facet
    """

    return await get_one_facet(
        c=request_wide_bulk.connector,
        facetid=facetid,
        orgid=orgid,
        facet=await request_wide_bulk.get_lora_object(
            type_=LoraObjectType.facet, uuid=facetid
        ),
        data=data,
    )


async def get_facetids(facet: str):
    c = common.get_connector()

    uuid, bvn = (facet, None) if util.is_uuid(facet) else (None, facet)

    facetids = await c.facet.load_uuids(uuid=uuid, bvn=bvn, publiceret="Publiceret")

    if not facetids:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_NOT_FOUND,
            message=f"Facet {facet} not found.",
        )

    assert len(facetids) <= 1, "Facet is not unique"

    return facetids


# TODO: Refactored and moved below code to appropriate place


async def get_sorted_primary_class_list(c: lora.Connector) -> list[tuple[str, int]]:
    """
    Return a list of primary classes, sorted by priority in the "scope" field

    :param c: A LoRa connector
    :return: A sorted list of tuples of (uuid, scope) for all available primary classes
    """
    facet_id = (await c.facet.load_uuids(bvn="primary_type"))[0]

    classes = await gather(
        *[
            create_task(clazz.get_one_class_full(c, class_id, class_obj))
            for class_id, class_obj in (await c.klasse.get_all(facet=facet_id))
        ]
    )

    # We always expect the scope value to be an int, for sorting
    try:
        parsed_classes = [(clazz["uuid"], int(clazz["scope"])) for clazz in classes]
    except ValueError:
        raise ErrorCodes.E_INTERNAL_ERROR(
            message="Unable to parse scope value as integer"
        )

    # Sort based on scope values, higher is better
    sorted_classes = sorted(parsed_classes, key=lambda x: x[1], reverse=True)

    return sorted_classes


def is_class_primary(mo_class: dict) -> bool:
    try:
        return int(mo_class[mapping.SCOPE]) >= mapping.MINIMUM_PRIMARY_SCOPE_VALUE
    except KeyError:
        logging.error(f"Primary class has no 'scope' {mo_class=}")
        return False
    except ValueError:
        logging.error(f"Primary class has a non-integer value in 'scope', {mo_class=}")
        return False


async def is_class_uuid_primary(primary_class_uuid: str) -> bool:
    # Determine whether the given `primary_class_uuid` does indeed refer to a
    # primary class (as opposed to a non-primary class.)
    connector = lora.Connector()
    mo_class = await clazz.get_one_class(connector, primary_class_uuid)
    if (mo_class is None) or (not is_class_primary(mo_class)):
        return False
    return True


async def get_mo_object_primary_value(mo_object: dict) -> bool:
    primary = mo_object.get(mapping.PRIMARY) or {}
    if mapping.SCOPE in primary:
        return is_class_primary(mo_object[mapping.PRIMARY])

    # Next, see if `mo_object` contains a `primary` dict with a `uuid` key
    try:
        primary_class_uuid = util.get_mapping_uuid(mo_object, mapping.PRIMARY)
    except exceptions.HTTPException:
        # Raised by `get_mapping_uuid` in case there is no UUID
        return False
    else:
        return await is_class_uuid_primary(primary_class_uuid)


class ClassRequestHandler(handlers.RequestHandler):
    role_type = "class"

    async def prepare_create(self, request: dict):
        valid_from = util.NEGATIVE_INFINITY
        valid_to = util.POSITIVE_INFINITY

        facet_bvn = request["facet"]
        facetids = await get_facetids(facet_bvn)
        facet_uuid = one(facetids)

        mo_class = request["class_model"]

        clazz = common.create_klasse_payload(
            valid_from=valid_from,
            valid_to=valid_to,
            facet_uuid=facet_uuid,
            org_uuid=mo_class.org_uuid,
            owner=mo_class.owner,
            bvn=mo_class.user_key,
            title=mo_class.name,
            scope=mo_class.scope,
        )

        self.payload = clazz
        self.uuid = mo_class.uuid or str(uuid4())

    async def submit(self) -> str:
        c = lora.Connector()

        if self.request_type == mapping.RequestType.CREATE:
            self.result = await c.klasse.create(self.payload, self.uuid)
        else:
            self.result = await c.klasse.update(self.payload, self.uuid)

        return await super().submit()


@router.post("/f/{facet}/")
async def create_or_update_class(
    facet: str,
    class_model: ClassWrite,
):
    """Will create a new class if there's no UUID or it doesnt match an exiting class
    Will update an existing class if there's a matching UUID

    :param facet: One of the facet bvns/uuids.
    :param class_model: Pydantic BaseModel for a class
    """
    req = {"facet": facet, "class_model": class_model}
    request = await ClassRequestHandler.construct(req, mapping.RequestType.CREATE)
    return await request.submit()


@router.get("/c/ancestor-tree")
async def get_class_ancestor_tree(
    uuid: list[UUID] | None = None, only_primary_uuid: bool | None = None
):
    """Obtain the tree of ancestors for the given classes.

    The tree includes siblings of ancestors:

    * Every ancestor of each class.
    * Every sibling of every ancestor.

    The intent of this routine is to enable easily showing the tree
    *up to and including* the given classes in the UI.

    .. :quickref: Class; Ancestor tree

    :queryparam uuid: The UUID of the class.

    :see: http:get:`/service/c/(uuid:uuid)/`.

    **Example Response**:

    .. sourcecode:: json

     [{
        "children": [{
            "children": [{
                "name": "Industrigruppen",
                "user_key": "LO_3f_industri",
                "uuid": "71acc2cf-9a4f-465d-80b7-d6ba4d823ac5",
                "...": "..."
            }],
            "name": "Fagligt Fælles Forbund (3F)",
            "user_key": "LO_3f",
            "uuid": "87fc0429-ab51-4b5a-bad2-f55ba39f88d2",
            "...": "..."
        }],
        "name": "LO",
        "user_key": "LO",
        "uuid": "a966e536-998a-42b7-9213-c9f89b27f8f8",
        "...": "..."
     }]
    """

    if uuid is None:
        return []

    c = common.get_connector()
    classids = uuid

    return await clazz.get_class_tree(
        c, classids, with_siblings=True, only_primary_uuid=only_primary_uuid
    )

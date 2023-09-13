# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""
Classes
------

This sections describes how to interact with classes.
NOTE the file is named `clazz` to avoid conflict with the Python keyword `class`.

"""
import enum
import locale
from asyncio import create_task
from asyncio import gather
from collections.abc import Awaitable
from typing import Any
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter
from more_itertools import one

from . import facet
from . import handlers
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..exceptions import ErrorCodes
from ..lora import LoraObjectType
from .tree_helper import prepare_ancestor_tree
from mora.request_scoped.bulking import request_wide_bulk
from ramodels.mo.class_ import ClassWrite


router = APIRouter()


# Main class details class


@enum.unique
class ClassDetails(enum.Enum):  # TODO: Deal with cross-language enums
    # full class name
    FULL_NAME = 0
    # with child count
    NCHILDREN = 1
    TOP_LEVEL_FACET = 2
    FACET = 3


# Class request handler


class ClassRequestHandler(handlers.RequestHandler):
    role_type = "class"

    async def prepare_create(self, request: dict):
        valid_from = util.NEGATIVE_INFINITY
        valid_to = util.POSITIVE_INFINITY

        facet_bvn = request["facet"]
        facetids = await facet.get_facetids(facet_bvn)
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


# Constants

MO_OBJ_TYPE = dict[str, Any]
FULL_DETAILS = {
    ClassDetails.FACET,
    ClassDetails.FULL_NAME,
    ClassDetails.TOP_LEVEL_FACET,
}


# Methods


def is_class_reg_valid(reg):
    return any(state.get("publiceret") == "Aktiv" for state in util.get_states(reg))


def is_class_primary(mo_class: dict) -> bool:
    try:
        return mo_class[mapping.USER_KEY] in (
            mapping.PRIMARY,
            mapping.EXPLICITLY_PRIMARY,
        )
    except KeyError:
        return False


async def get_one_class(
    c: lora.Connector,
    classid,
    clazz=None,
    details: set[ClassDetails] | None = None,
    only_primary_uuid: bool = False,
    validity=None,
) -> MO_OBJ_TYPE:
    if not details:
        details = set()

    if only_primary_uuid:
        return {mapping.UUID: classid}

    if not clazz:  # optionally exit early
        if not classid:
            return None

        clazz = await c.klasse.get(classid)

        if not clazz:
            return None

    attrs = _get_attrs(clazz)
    parents = None

    owner = _get_owner_uuid(clazz)

    response = {
        "uuid": classid,
        "name": attrs.get("titel"),
        "user_key": attrs.get("brugervendtnoegle"),
        "example": attrs.get("eksempel"),
        "scope": attrs.get("omfang"),
        "owner": owner,
        "org_uuid": _get_class_org_uuid(clazz),
        "facet_uuid": _get_class_facet_uuid(clazz),
    }

    # create tasks
    if ClassDetails.FACET in details:
        facet_task = create_task(_get_facet(clazz))

    if ClassDetails.NCHILDREN in details:
        nchildren_task = create_task(count_class_children(c, classid))

    if ClassDetails.FULL_NAME in details or ClassDetails.TOP_LEVEL_FACET in details:
        if not parents:
            parents = await _get_parents(clazz)

        if ClassDetails.FULL_NAME in details:
            response["full_name"] = _get_full_name(parents)

        if ClassDetails.TOP_LEVEL_FACET in details:
            response["top_level_facet"] = await _get_top_level_facet(parents)

    if ClassDetails.FACET in details:
        response["facet"] = await facet_task

    if ClassDetails.NCHILDREN in details:
        response["child_count"] = await nchildren_task

    validities = clazz["tilstande"]["klassepubliceret"]
    # TODO: Figure out the correct way instead of just using [0]
    response["published"] = validities[0]["publiceret"]
    response[mapping.VALIDITY] = validity or util.get_effect_validity(validities[0])

    return response


async def get_one_class_full(*args, only_primary_uuid: bool = False, **kwargs):
    """Helper function for reading classes enriched with additional details"""
    return await get_one_class(
        *args, **kwargs, details=FULL_DETAILS, only_primary_uuid=only_primary_uuid
    )


async def get_sorted_primary_class_list(c: lora.Connector) -> list[tuple[str, int]]:
    """
    Return a list of primary classes, sorted by priority in the "scope" field

    :param c: A LoRa connector
    :return: A sorted list of tuples of (uuid, scope) for all available primary classes
    """
    facet_id = (await c.facet.load_uuids(bvn="primary_type"))[0]

    classes = await gather(
        *[
            create_task(get_one_class_full(c, class_id, class_obj))
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


async def get_class_tree(
    c, classids: list[UUID], with_siblings=False, only_primary_uuid: bool = False
):
    """Return a tree, bounded by the given classid.

    The tree includes siblings of ancestors, with their child counts.
    """

    async def get_class(classid):
        r = await get_one_class(
            c,
            classid,
            cache[classid],
            details=(
                {ClassDetails.NCHILDREN}
                if with_siblings and classid not in children
                else None
            ),
            only_primary_uuid=only_primary_uuid,
        )
        if classid in children:
            r["children"] = await get_classes(children[classid])
        return r

    async def get_classes(classids):
        classes = await gather(*[create_task(get_class(cid)) for cid in classids])
        return sorted(
            classes,
            key=lambda u: locale.strxfrm(u[mapping.NAME]),
        )

    def get_children_args(uuid, parent_uuid, cache):
        return {"overordnetklasse": parent_uuid}

    root_uuids, children, cache = await prepare_ancestor_tree(
        c.klasse,
        mapping.PARENT_CLASS_FIELD,
        classids,
        get_children_args,
        with_siblings=with_siblings,
    )
    return await get_classes(root for root in root_uuids)


async def get_mo_object_primary_value(mo_object: dict) -> bool:
    # First, see if `mo_object` contains a `primary` dict with a `user_key` key
    primary = mo_object.get(mapping.PRIMARY) or {}
    if mapping.USER_KEY in primary:
        return is_class_primary(mo_object[mapping.PRIMARY])

    # Next, see if `mo_object` contains a `primary` dict with a `uuid` key
    try:
        primary_class_uuid = util.get_mapping_uuid(mo_object, mapping.PRIMARY)
    except exceptions.HTTPException:
        # Raised by `get_mapping_uuid` in case there is no UUID
        return False
    else:
        return await is_class_uuid_primary(primary_class_uuid)


async def fetch_class_children(c, parent_uuid) -> list:
    return list(
        await c.klasse.get_all(publiceret="Publiceret", overordnetklasse=parent_uuid)
    )


async def count_class_children(c, parent_uuid):
    """Find the number of children under the class given by uuid."""
    return len(await fetch_class_children(c, parent_uuid))


async def request_bulked_get_one_class(
    classid: str,
    details: set[ClassDetails] | None = None,
    only_primary_uuid: bool = False,
) -> Awaitable[MO_OBJ_TYPE]:
    """
    EAGERLY adds a uuid to a LAZILY-processed cache. Return an awaitable. Once the
    result is awaited, the FULL cache is processed. Useful to 'under-the-hood' bulk.

    :param classid: uuid of class
    :param details: configure processing of the class
    :param only_primary_uuid:
    :return: Awaitable returning the processed class
    """
    return _get_class_from_cache(
        classid=classid, details=details, only_primary_uuid=only_primary_uuid
    )


async def request_bulked_get_one_class_full(
    classid: str, only_primary_uuid: bool = False
) -> Awaitable[MO_OBJ_TYPE]:
    """
    trivial wrapper for often-used setting
    :param classid: uuid of class
    :param only_primary_uuid:
    :return: Awaitable returning the processed class
    """
    return await request_bulked_get_one_class(
        classid=classid, details=FULL_DETAILS, only_primary_uuid=only_primary_uuid
    )


async def is_class_uuid_primary(primary_class_uuid: str) -> bool:
    # Determine whether the given `primary_class_uuid` does indeed refer to a
    # primary class (as opposed to a non-primary class.)
    connector = lora.Connector()
    mo_class = await get_one_class(connector, primary_class_uuid)
    if (mo_class is None) or (not is_class_primary(mo_class)):
        return False
    return True


# PROTECTEDs


def _get_attrs(clazz):
    return clazz["attributter"]["klasseegenskaber"][0]


def _get_parent(clazz):
    """Find the parent UUID of the provided class object."""
    for parentid in mapping.PARENT_CLASS_FIELD.get_uuids(clazz):
        return parentid


def _get_class_org_uuid(clazz):
    return clazz["relationer"]["ansvarlig"][0]["uuid"]


def _get_class_facet_uuid(clazz):
    return clazz["relationer"]["facet"][0]["uuid"]


def _get_owner_uuid(clazz):
    rel = clazz["relationer"]
    return rel["ejer"][0]["uuid"] if "ejer" in rel else None


def _get_full_name(parents):
    full_name = " - ".join(
        [_get_attrs(clazz).get("titel") for clazz in reversed(parents)]
    )
    return full_name


async def _get_parents(clazz):
    potential_parent = _get_parent(clazz)
    if potential_parent is None:
        return [clazz]
    new_class = await request_wide_bulk.get_lora_object(
        type_=LoraObjectType.class_, uuid=potential_parent
    )
    return [clazz] + await _get_parents(new_class)


async def _get_top_level_facet(parents):
    facetid = _get_class_facet_uuid(parents[-1])
    return await facet.get_facet_from_cache(facetid=facetid)


async def _get_facet(clazz):
    facetid = _get_class_facet_uuid(clazz)
    return await facet.get_facet_from_cache(facetid=facetid)


async def _get_class_from_cache(
    classid: str,
    details: set[ClassDetails] | None = None,
    only_primary_uuid: bool = False,
) -> MO_OBJ_TYPE:
    """
    Get org unit from cache and process it
    :param classid: uuid of class
    :param details: configure processing of the class
    :param only_primary_uuid:
    :return: A processed class
    """
    return await get_one_class(
        c=request_wide_bulk.connector,
        classid=classid,
        clazz=await request_wide_bulk.get_lora_object(
            type_=LoraObjectType.class_, uuid=classid
        )
        if not only_primary_uuid
        else None,
        details=details,
        only_primary_uuid=only_primary_uuid,
    )


# ROUTEs
# TODO: find the correct place for these - they where just moved to this file
# from "mora.service.facets" when making no-static classes


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

    return await get_class_tree(
        c, classids, with_siblings=True, only_primary_uuid=only_primary_uuid
    )


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

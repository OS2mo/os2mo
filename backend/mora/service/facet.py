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

MO_OBJ_TYPE = dict[str, Any]


@enum.unique
class ClassDetails(enum.Enum):  # TODO: Deal with cross-language enums
    # full class name
    FULL_NAME = 0
    # with child count
    NCHILDREN = 1
    TOP_LEVEL_FACET = 2
    FACET = 3


FULL_DETAILS = {
    ClassDetails.FACET,
    ClassDetails.FULL_NAME,
    ClassDetails.TOP_LEVEL_FACET,
}


@router.get("/c/ancestor-tree")
# @util.restrictargs('at', 'uuid')
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

    c = common.get_connector()
    classids = uuid

    return await get_class_tree(
        c, classids, with_siblings=True, only_primary_uuid=only_primary_uuid
    )


async def get_class_tree(
    c, classids, with_siblings=False, only_primary_uuid: bool = False
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


async def __get_facet_from_cache(facetid, orgid=None, data=None) -> Any:
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


async def get_one_facet(c, facetid, orgid=None, facet=None, data=None):
    """Fetch a facet and enrich it."""

    # Use given facet or fetch one, if none is given
    facet = facet or (await c.facet.get(facetid))
    if facet is None:
        return None

    properties = facet["attributter"]["facetegenskaber"][0]
    bvn = properties["brugervendtnoegle"]
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


async def fetch_class_children(c, parent_uuid) -> list:
    return list(
        await c.klasse.get_all(publiceret="Publiceret", overordnetklasse=parent_uuid)
    )


async def count_class_children(c, parent_uuid):
    """Find the number of children under the class given by uuid."""
    return len(await fetch_class_children(c, parent_uuid))


async def __get_class_from_cache(
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
    return __get_class_from_cache(
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


async def get_one_class(
    c: lora.Connector,
    classid,
    clazz=None,
    details: set[ClassDetails] | None = None,
    only_primary_uuid: bool = False,
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

    def get_attrs(clazz):
        return clazz["attributter"]["klasseegenskaber"][0]

    attrs = get_attrs(clazz)
    parents = None

    def get_parent(clazz):
        """Find the parent UUID of the provided class object."""
        for parentid in mapping.PARENT_CLASS_FIELD.get_uuids(clazz):
            return parentid

    def get_facet_uuid(clazz):
        return clazz["relationer"]["facet"][0]["uuid"]

    def get_owner_uuid(clazz):
        rel = clazz["relationer"]
        return rel["ejer"][0]["uuid"] if "ejer" in rel else None

    def get_full_name(parents):
        full_name = " - ".join(
            [get_attrs(clazz).get("titel") for clazz in reversed(parents)]
        )
        return full_name

    async def get_parents(clazz):
        potential_parent = get_parent(clazz)
        if potential_parent is None:
            return [clazz]
        new_class = await request_wide_bulk.get_lora_object(
            type_=LoraObjectType.class_, uuid=potential_parent
        )
        return [clazz] + await get_parents(new_class)

    async def get_top_level_facet(parents):
        facetid = get_facet_uuid(parents[-1])
        return await __get_facet_from_cache(facetid=facetid)

    async def get_facet(clazz):
        facetid = get_facet_uuid(clazz)
        return await __get_facet_from_cache(facetid=facetid)

    owner = get_owner_uuid(clazz)

    response = {
        "uuid": classid,
        "name": attrs.get("titel"),
        "user_key": attrs.get("brugervendtnoegle"),
        "example": attrs.get("eksempel"),
        "scope": attrs.get("omfang"),
        "owner": owner,
    }

    # create tasks
    if ClassDetails.FACET in details:
        facet_task = create_task(get_facet(clazz))

    if ClassDetails.NCHILDREN in details:
        nchildren_task = create_task(count_class_children(c, classid))

    if ClassDetails.FULL_NAME in details or ClassDetails.TOP_LEVEL_FACET in details:
        if not parents:
            parents = await get_parents(clazz)

        if ClassDetails.FULL_NAME in details:
            response["full_name"] = get_full_name(parents)

        if ClassDetails.TOP_LEVEL_FACET in details:
            response["top_level_facet"] = await get_top_level_facet(parents)

    if ClassDetails.FACET in details:
        response["facet"] = await facet_task

    if ClassDetails.NCHILDREN in details:
        response["child_count"] = await nchildren_task

    return response


# Helper function for reading classes enriched with additional details
async def get_one_class_full(*args, only_primary_uuid: bool = False, **kwargs):
    return await get_one_class(
        *args, **kwargs, details=FULL_DETAILS, only_primary_uuid=only_primary_uuid
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


def is_class_primary(mo_class: dict) -> bool:
    try:
        return mo_class[mapping.USER_KEY] in (
            mapping.PRIMARY,
            mapping.EXPLICITLY_PRIMARY,
        )
    except KeyError:
        return False


async def is_class_uuid_primary(primary_class_uuid: str) -> bool:
    # Determine whether the given `primary_class_uuid` does indeed refer to a
    # primary class (as opposed to a non-primary class.)
    connector = lora.Connector()
    mo_class = await get_one_class(connector, primary_class_uuid)
    if (mo_class is None) or (not is_class_primary(mo_class)):
        return False
    return True


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

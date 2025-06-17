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
import logging
from functools import partial
from typing import Any
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter
from more_itertools import last
from more_itertools import one
from ramodels.mo.class_ import ClassWrite

from mora.request_scoped.bulking import get_lora_object

from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..exceptions import ErrorCodes
from ..graphapi.middleware import is_graphql
from ..lora import LoraObjectType
from . import handlers
from .tree_helper import prepare_ancestor_tree

logger = logging.getLogger(__name__)

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
):  # pragma: no cover
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

    with_siblings = True

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
        classes = [await get_class(cid) for cid in classids]
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


async def get_one_facet(c, facetid, facet=None, extended: bool = False, validity=None):
    """Fetch a facet and enrich it."""

    # Use given facet or fetch one, if none is given
    facet = facet or (await c.facet.get(facetid))
    if facet is None:  # pragma: no cover
        return None

    properties = facet["attributter"]["facetegenskaber"][0]
    bvn = properties["brugervendtnoegle"]
    description = properties.get("beskrivelse", "")
    response = {
        "uuid": facetid,
        "user_key": bvn,
        "description": description,
    }

    if extended:
        response["org_uuid"] = facet["relationer"]["ansvarlig"][0]["uuid"]
        validities = facet["tilstande"]["facetpubliceret"]
        response[mapping.VALIDITY] = validity or util.get_effect_validity(validities[0])

        response["published"] = validities[0]["publiceret"]

    return response


async def request_bulked_get_one_class(
    classid: str,
    details: set[ClassDetails] | None = None,
    only_primary_uuid: bool = False,
    connector: lora.Connector | None = None,
) -> MO_OBJ_TYPE:
    if connector is None:
        connector = common.get_connector()
    return await get_one_class(
        c=connector,
        classid=classid,
        clazz=await get_lora_object(
            type_=LoraObjectType.class_, uuid=classid, connector=connector
        )
        if not only_primary_uuid
        else None,
        details=details,
        only_primary_uuid=only_primary_uuid,
    )


request_bulked_get_one_class_full = partial(
    request_bulked_get_one_class, details=FULL_DETAILS
)


async def get_one_class(
    c: lora.Connector,
    classid,
    clazz=None,
    details: set[ClassDetails] | None = None,
    only_primary_uuid: bool = False,
    extended: bool = False,
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

    def get_attrs(clazz):
        return clazz["attributter"]["klasseegenskaber"][0]

    attrs = get_attrs(clazz)
    parents = None

    def get_parent(clazz):
        """Find the parent UUID of the provided class object."""
        for parentid in mapping.PARENT_CLASS_FIELD.get_uuids(clazz):  # pragma: no cover
            return parentid

    def get_facet_uuid(clazz):
        return clazz["relationer"]["facet"][0]["uuid"]

    def get_owner_uuid(clazz):
        rel = clazz["relationer"]
        return rel["ejer"][0]["uuid"] if rel.get("ejer") else None

    def get_full_name(parents):
        full_name = " - ".join(
            [get_attrs(clazz).get("titel") for clazz in reversed(parents)]
        )
        return full_name

    async def get_parents(clazz):
        potential_parent = get_parent(clazz)
        if potential_parent is None:
            return [clazz]
        # coverage: pause
        new_class = await get_lora_object(
            type_=LoraObjectType.class_, uuid=potential_parent
        )
        return [clazz] + await get_parents(new_class)
        # coverage: unpause

    async def getfacet(facetid) -> Any:
        """
        Get org unit from cache and process it
        :param facetid: uuid of facet
        :return: A processed facet
        """
        connector = common.get_connector()
        facet = await get_lora_object(
            type_=LoraObjectType.facet, uuid=facetid, connector=connector
        )
        return await get_one_facet(c=connector, facetid=facetid, facet=facet)

    async def get_top_level_facet(parents):
        facetid = get_facet_uuid(parents[-1])
        return await getfacet(facetid=facetid)

    async def get_facet(clazz):
        facetid = get_facet_uuid(clazz)
        return await getfacet(facetid=facetid)

    async def count_class_children(c, parent_uuid):  # pragma: no cover
        """Find the number of children under the class given by uuid."""
        return len(
            list(
                await c.klasse.get_all(
                    publiceret="Publiceret", overordnetklasse=parent_uuid
                )
            )
        )

    owner = get_owner_uuid(clazz)

    response = {
        "uuid": classid,
        "name": attrs.get("titel"),
        "user_key": attrs.get("brugervendtnoegle"),
        "example": attrs.get("eksempel"),
        "scope": attrs.get("omfang"),
        "owner": owner,
        # TODO(#52443): don't last()
        "published": last(clazz["tilstande"]["klassepubliceret"])["publiceret"],
    }

    if ClassDetails.FULL_NAME in details or ClassDetails.TOP_LEVEL_FACET in details:
        if not parents:
            parents = await get_parents(clazz)

        if ClassDetails.FULL_NAME in details:
            response["full_name"] = get_full_name(parents)

        if ClassDetails.TOP_LEVEL_FACET in details:
            response["top_level_facet"] = await get_top_level_facet(parents)

    if ClassDetails.FACET in details:
        response["facet"] = await get_facet(clazz)

    if ClassDetails.NCHILDREN in details:  # pragma: no cover
        response["child_count"] = await count_class_children(c, classid)

    if extended:
        response["facet_uuid"] = get_facet_uuid(clazz)
        response["org_uuid"] = last(clazz["relationer"]["ansvarlig"])["uuid"]
        validities = clazz["tilstande"]["klassepubliceret"]
        response[mapping.VALIDITY] = validity or util.get_effect_validity(validities[0])

    if is_graphql():
        response["description"] = attrs.get("beskrivelse")
        response["parent_uuid"] = last(
            mapping.PARENT_CLASS_FIELD.get_uuids(clazz), default=None
        )
        response["it_system_uuid"] = last(
            clazz["relationer"].get("mapninger", []), default={}
        ).get("uuid")

    return response


async def get_sorted_primary_class_list(c: lora.Connector) -> list[tuple[str, int]]:
    """
    Return a list of primary classes, sorted by priority in the "scope" field

    :param c: A LoRa connector
    :return: A sorted list of tuples of (uuid, scope) for all available primary classes
    """
    get_one_class_full = partial(get_one_class, details=FULL_DETAILS)

    facet_id = (await c.facet.load_uuids(bvn="primary_type"))[0]

    classes = [
        await get_one_class_full(c, class_id, class_obj)
        for class_id, class_obj in (await c.klasse.get_all(facet=facet_id))
    ]

    # We always expect the scope value to be an int, for sorting
    try:
        parsed_classes = [(clazz["uuid"], int(clazz["scope"])) for clazz in classes]
    except ValueError:  # pragma: no cover
        raise ErrorCodes.E_INTERNAL_ERROR(
            message="Unable to parse scope value as integer"
        )

    # Sort based on scope values, higher is better
    sorted_classes = sorted(parsed_classes, key=lambda x: x[1], reverse=True)

    return sorted_classes


class ClassRequestHandler(handlers.RequestHandler):
    role_type = "class"

    async def prepare_create(self, request: dict):
        async def get_facetids(facet: str):
            c = common.get_connector()

            uuid, bvn = (facet, None) if util.is_uuid(facet) else (None, facet)

            facetids = await c.facet.load_uuids(
                uuid=uuid, bvn=bvn, publiceret="Publiceret"
            )

            if not facetids:  # pragma: no cover
                raise exceptions.HTTPException(
                    exceptions.ErrorCodes.E_NOT_FOUND,
                    message=f"Facet {facet} not found.",
                )

            assert len(facetids) <= 1, "Facet is not unique"

            return facetids

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
        else:  # pragma: no cover
            self.result = await c.klasse.update(self.payload, self.uuid)
        # coverage: pause
        return await super().submit()
        # coverage: unpause


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
    mo_class = await get_one_class(connector, primary_class_uuid)
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

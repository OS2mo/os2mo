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
import logging
from functools import partial
from typing import Any

from fastapi import APIRouter
from more_itertools import first
from more_itertools import last

from mora.request_scoped.bulking import get_lora_object

from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..exceptions import ErrorCodes
from ..graphapi.middleware import is_graphql
from ..lora import LoraObjectType

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
        for parentid in mapping.PARENT_CLASS_FIELD.get_uuids(clazz):
            return parentid  # pragma: no cover

    def get_facet_uuid(clazz):
        return clazz["relationer"]["facet"][0]["uuid"]

    def get_owner_uuid(clazz):
        owner = first(clazz["relationer"].get("ejer", []), default={})
        # LoRa represents cleared relations as {uuid: "", urn: ""}
        return owner.get("uuid") or None

    def get_full_name(parents):
        full_name = " - ".join(
            [get_attrs(clazz).get("titel") for clazz in reversed(parents)]
        )
        return full_name

    async def get_parents(clazz):
        potential_parent = get_parent(clazz)
        if potential_parent is None:
            return [clazz]
        new_class = await get_lora_object(  # pragma: no cover
            type_=LoraObjectType.class_, uuid=potential_parent
        )
        return [clazz] + await get_parents(new_class)  # pragma: no cover

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

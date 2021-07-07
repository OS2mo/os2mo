# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

'''
Facets
------

This sections describes how to interact with facets, i.e. the types of
objects.

    .. http:>jsonarr string name:: Human-readable name.
    .. http:>jsonarr string uuid:: Machine-friendly UUID.
    .. http:>jsonarr string user_key:: Short, unique key.
    .. http:>jsonarr string example:: An example value for the address field.
        A value of `<UUID>` means that this is a `DAR`_ address UUID.

'''

import enum
import locale
from asyncio import create_task, gather
from uuid import UUID, uuid4
from more_itertools import one
from typing import Any, Awaitable, Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, Request

from mora.request_scoped.bulking import request_wide_bulk
from mora.service.models import MOClass
import mora.async_util
from . import handlers
from .tree_helper import prepare_ancestor_tree
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from ..exceptions import ErrorCodes
from ..lora import LoraObjectType

router = APIRouter()

MO_OBJ_TYPE = Dict[str, Any]


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
    ClassDetails.TOP_LEVEL_FACET
}


@router.get('/c/ancestor-tree')
# @util.restrictargs('at', 'uuid')
async def get_class_ancestor_tree(
    uuid: Optional[List[UUID]] = None,
    only_primary_uuid: Optional[bool] = None
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


async def get_class_tree(c, classids, with_siblings=False,
                         only_primary_uuid: bool = False):
    """Return a tree, bounded by the given classid.

    The tree includes siblings of ancestors, with their child counts.
    """

    async def get_class(classid):
        r = await get_one_class(
            c, classid, cache[classid],
            details=(
                {ClassDetails.NCHILDREN}
                if with_siblings and classid not in children
                else None
            ), only_primary_uuid=only_primary_uuid,
        )
        if classid in children:
            r['children'] = await get_classes(children[classid])
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
        with_siblings=with_siblings
    )
    return await get_classes(root for root in root_uuids)


@router.get('/c/{classid}/')
# @util.restrictargs('limit', 'start')
async def get_class(
    classid: UUID,
    only_primary_uuid: Optional[bool] = None
):
    """Get class by UUID.

    :queryparam uuid: The UUID of the class.

    **Example Response**:

    .. sourcecode:: json

     {
         "name": "Industrigruppen",
         "user_key": "LO_3f_industri",
         "uuid": "71acc2cf-9a4f-465d-80b7-d6ba4d823ac5"
         "...": "..."
     }
    """
    classid = str(classid)

    c = common.get_connector()
    class_details = map_query_args_to_class_details(util.get_query_args())

    return await get_one_class(
        c, classid, details=class_details, only_primary_uuid=only_primary_uuid
    )


async def prepare_class_child(c, entry):
    """Minimize and enrich JSON, by only returning relevant data."""
    return {
        'child_count': await count_class_children(c, entry['uuid']),
        'name': entry['name'],
        'user_key': entry['user_key'],
        'uuid': entry['uuid']
    }


@router.get('/c/{classid}/children')
# @util.restrictargs('limit', 'start')
async def get_all_class_children(
    classid: UUID,
    only_primary_uuid: Optional[bool] = None
):
    """Get class children by UUID.

    :queryparam uuid: The UUID of the class.

    **Example Response**:

    .. sourcecode:: json

     [{
        "child_count":6,
        "name":"Fagligt F\u00e6lles Forbund (3F)",
        "user_key":"LO_3f",
        "uuid":"87fc0429-ab51-4b5a-bad2-f55ba39f88d2"
     },{
        "child_count":0,
        "name":"F\u00e6ngselsforbundet i Danmark",
        "user_key":"LO_jail",
        "uuid":"31b2424b-9fb3-43c4-b068-b75a1b086ee8"
     }]
    """
    classid = str(classid)

    c = common.get_connector()

    classes = await fetch_class_children(c, classid)
    classes = await gather(
        *[create_task(get_one_class(c, *tup, only_primary_uuid=only_primary_uuid)) for
          tup in classes]
    )
    classes = await gather(
        *[create_task(prepare_class_child(c, class_)) for class_ in classes]
    )

    return sorted(
        classes,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f['name']) if f.get('name') else '',
    )


@router.get('/o/{orgid}/f/')
# @util.restrictargs()
async def list_facets(orgid: UUID):
    '''List the facet types available in a given organisation.

    :param uuid orgid: Restrict search to this organisation.

    .. :quickref: Facet; List types

    :>jsonarr string name: The facet name.
    :>jsonarr string path: The location on the web server.
    :>jsonarr string user_key: Short, unique key identifying the facet
    :>jsonarr string uuid: The UUID of the facet.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "address",
          "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address/",
          "user_key": "Adressetype",
          "uuid": "e337bab4-635f-49ce-aa31-b44047a43aa1"
        },
        {
          "name": "ou",
          "path": "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/ou/",
          "user_key": "Enhedstype",
          "uuid": "fc917e7c-fc3b-47c2-8aa5-a0383342a280"
        }
      ]

    '''
    orgid = str(orgid)

    c = common.get_connector()

    async def transform(facet_tuple):
        facetid, facet = facet_tuple
        return await get_one_facet(c, facetid, orgid, facet)

    response = await c.facet.get_all(ansvarlig=orgid, publiceret='Publiceret')
    response = await gather(
        *[create_task(transform(facet_tuple)) for facet_tuple in response]
    )

    return sorted(
        response,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f['name']) if f.get('name') else '',
    )


async def __get_facet_from_cache(facetid, orgid=None, data=None) -> Any:
    """
    Get org unit from cache and process it
    :param facetid: uuid of facet
    :param facet:
    :param data:
    :return: A processed facet
    """

    return await get_one_facet(c=request_wide_bulk.connector,
                               facetid=facetid,
                               orgid=orgid,
                               facet=await request_wide_bulk.get_lora_object(
                                   type_=LoraObjectType.facet, uuid=facetid),
                               data=data)


async def get_one_facet(c, facetid, orgid=None, facet=None, data=None):
    """Fetch a facet and enrich it."""

    # Use given facet or fetch one, if none is given
    facet = facet or (await c.facet.get(facetid))
    if facet is None:
        return None

    properties = facet['attributter']['facetegenskaber'][0]
    bvn = properties['brugervendtnoegle']
    description = properties.get("beskrivelse", '')
    response = {
        'uuid': facetid,
        'user_key': bvn,
        'description': description,
    }
    if orgid:
        response['path'] = (bvn and router.url_path_for(
            'get_classes', orgid=orgid, facet=bvn
        ))
    if data:
        response['data'] = data
    return response


async def fetch_class_children(c, parent_uuid) -> List:
    return list(
        await c.klasse.get_all(publiceret='Publiceret', overordnetklasse=parent_uuid)
    )


async def count_class_children(c, parent_uuid):
    """Find the number of children under the class given by uuid."""
    return len(await fetch_class_children(c, parent_uuid))


async def __get_class_from_cache(classid: str,
                                 details: Optional[Set[ClassDetails]] = None,
                                 only_primary_uuid: bool = False
                                 ) -> MO_OBJ_TYPE:
    """
    Get org unit from cache and process it
    :param classid: uuid of class
    :param details: configure processing of the class
    :param only_primary_uuid:
    :return: A processed class
    """
    return await get_one_class(c=request_wide_bulk.connector, classid=classid,
                               clazz=await request_wide_bulk.get_lora_object(
                                   type_=LoraObjectType.class_,
                                   uuid=classid) if not only_primary_uuid else None,
                               details=details,
                               only_primary_uuid=only_primary_uuid)


async def request_bulked_get_one_class(classid: str,
                                       details: Optional[Set[ClassDetails]] = None,
                                       only_primary_uuid: bool = False
                                       ) -> Awaitable[MO_OBJ_TYPE]:
    """
    EAGERLY adds a uuid to a LAZILY-processed cache. Return an awaitable. Once the
    result is awaited, the FULL cache is processed. Useful to 'under-the-hood' bulk.

    :param classid: uuid of class
    :param details: configure processing of the class
    :param only_primary_uuid:
    :return: Awaitable returning the processed class
    """
    if not only_primary_uuid:
        await request_wide_bulk.add(type_=LoraObjectType.class_, uuid=classid)
    return __get_class_from_cache(classid=classid, details=details,
                                  only_primary_uuid=only_primary_uuid)


async def request_bulked_get_one_class_full(classid: str,
                                            only_primary_uuid: bool = False
                                            ) -> Awaitable[MO_OBJ_TYPE]:
    """
    trivial wrapper for often-used setting
    :param classid: uuid of class
    :param only_primary_uuid:
    :return: Awaitable returning the processed class
    """
    return await request_bulked_get_one_class(classid=classid, details=FULL_DETAILS,
                                              only_primary_uuid=only_primary_uuid)


async def get_one_class(c: lora.Connector, classid, clazz=None,
                        details: Optional[Set[ClassDetails]] = None,
                        only_primary_uuid: bool = False) -> MO_OBJ_TYPE:
    if not details:
        details = set()

    if only_primary_uuid:
        return {
            mapping.UUID: classid
        }

    if not clazz:  # optionally exit early
        if not classid:
            return None

        clazz = await c.klasse.get(classid)

        if not clazz:
            return None

    def get_attrs(clazz):
        return clazz['attributter']['klasseegenskaber'][0]

    attrs = get_attrs(clazz)
    parents = None

    utilize_request_wide_cache: bool = c is request_wide_bulk.connector

    def get_parent(clazz):
        """Find the parent UUID of the provided class object."""
        for parentid in mapping.PARENT_CLASS_FIELD.get_uuids(clazz):
            return parentid

    def get_facet_uuid(clazz):
        return clazz['relationer']['facet'][0]['uuid']

    def get_owner_uuid(clazz):
        rel = clazz['relationer']
        return rel['ejer'][0]['uuid'] if 'ejer' in rel else None

    def get_full_name(parents):
        full_name = " - ".join(
            [get_attrs(clazz).get('titel') for clazz in reversed(parents)])
        return full_name

    async def get_parents(clazz):
        potential_parent = get_parent(clazz)
        if potential_parent is None:
            return [clazz]
        new_class = await request_wide_bulk.get_lora_object(type_=LoraObjectType.class_,
                                                            uuid=potential_parent) if \
            utilize_request_wide_cache else await c.klasse.get(potential_parent)
        return [clazz] + await get_parents(new_class)

    async def get_top_level_facet(parents):
        facetid = get_facet_uuid(parents[-1])
        return await __get_facet_from_cache(facetid=facetid) if \
            utilize_request_wide_cache else await get_one_facet(c, facetid, orgid=None)

    async def get_facet(clazz):
        facetid = get_facet_uuid(clazz)
        return await __get_facet_from_cache(facetid=facetid) if \
            utilize_request_wide_cache else await get_one_facet(c, facetid, orgid=None)

    owner = get_owner_uuid(clazz)

    response = {
        'uuid': classid,
        'name': attrs.get('titel'),
        'user_key': attrs.get('brugervendtnoegle'),
        'example': attrs.get('eksempel'),
        'scope': attrs.get('omfang'),
        'owner': owner,
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
            response['full_name'] = get_full_name(parents)

        if ClassDetails.TOP_LEVEL_FACET in details:
            response['top_level_facet'] = await get_top_level_facet(parents)

    if ClassDetails.FACET in details:
        response['facet'] = await facet_task

    if ClassDetails.NCHILDREN in details:
        response['child_count'] = await nchildren_task

    return response


# Helper function for reading classes enriched with additional details
async def get_one_class_full(*args, only_primary_uuid: bool = False, **kwargs):
    return await get_one_class(*args, **kwargs, details=FULL_DETAILS,
                               only_primary_uuid=only_primary_uuid)


async def get_facetids(facet: str):
    c = common.get_connector()

    uuid, bvn = (facet, None) if util.is_uuid(facet) else (None, facet)

    facetids = await c.facet.fetch(
        uuid=uuid,
        bvn=bvn,
        publiceret='Publiceret'
    )

    if not facetids:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_NOT_FOUND,
            message="Facet {} not found.".format(facet)
        )

    assert len(facetids) <= 1, 'Facet is not unique'

    return facetids


async def get_classes_under_facet(orgid: UUID, facet: str,
                                  details: Set[ClassDetails] = None,
                                  only_primary_uuid: bool = False,
                                  start: int = 0,
                                  limit: int = 0):
    c = common.get_connector()

    facetids = await get_facetids(facet)

    async def getter_fn(*args, **kwargs):
        return await get_one_class(*args, **kwargs, details=details,
                                   only_primary_uuid=only_primary_uuid)

    return facetids and await get_one_facet(
        c,
        facetids[0],
        orgid,
        data=await c.klasse.paged_get(
            getter_fn,
            facet=facetids,
            publiceret='Publiceret',
            start=start, limit=limit
        )
    )


async def get_sorted_primary_class_list(c: lora.Connector) -> List[Tuple[str, int]]:
    """
    Return a list of primary classes, sorted by priority in the "scope" field

    :param c: A LoRa connector
    :return: A sorted list of tuples of (uuid, scope) for all available primary classes
    """
    facet_id = (await c.facet.fetch(bvn='primary_type'))[0]

    classes = await gather(*[
        create_task(get_one_class_full(c, class_id, class_obj,
                                       only_primary_uuid=False))
        for class_id, class_obj in (await c.klasse.get_all(facet=facet_id))
    ])

    # We always expect the scope value to be an int, for sorting
    try:
        parsed_classes = [(clazz['uuid'], int(clazz['scope'])) for clazz in classes]
    except ValueError:
        raise ErrorCodes.E_INTERNAL_ERROR(
            message="Unable to parse scope value as integer"
        )

    # Sort based on scope values, higher is better
    sorted_classes = sorted(parsed_classes, key=lambda x: x[1], reverse=True)

    return sorted_classes


@router.get('/o/{orgid}/f/{facet}/')
async def get_classes(
    orgid: UUID,
    facet: str,
    request: Request,
    start: Optional[int] = 0,
    limit: Optional[int] = 0,
    only_primary_uuid: Optional[bool] = None,
    at: Any = None,
    validity: Any = None,
):
    '''List classes available in the given facet.

    .. :quickref: Facet; Get

    :param uuid orgid: Restrict search to this organisation.
    :param string facet: One of the facet names listed by
        http:get:`/service/o/(uuid:orgid)/f/`

    :queryparam int start: Index of first item for paging.
    :queryparam int limit: Maximum items.

    :>jsonarr string name: Human-readable name.
    :>jsonarr string uuid: Machine-friendly UUID.
    :>jsonarr string user_key: Short, unique key.
    :>jsonarr string example: An example value. In most cases the
        value is meant to be presented to the user as an aid.
    :>jsonarr string scope: A representation of the type of value, see
        the table below for details.

    :status 200: On success.
    :status 404: Whenever the facet isn't found.

    **Example Response**:

    .. sourcecode:: json

      {
        "name": "address_type",
        "path":
          "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address_type/",
        "user_key": "Adressetype",
        "uuid": "e337bab4-635f-49ce-aa31-b44047a43aa1",
        "data": {
          "items": [
            {
              "example": "http://www.korsbaek.dk/",
              "name": "Hjemmeside",
              "scope": "WWW",
              "user_key": "URL",
              "uuid": "160ecaed-50b0-4800-bebc-0d0289a4f624"
            },
            {
              "example": "<UUID>",
              "name": "Lokation",
              "scope": "DAR",
              "user_key": "AdresseLokation",
              "uuid": "031f93c3-6bab-462e-a998-87cad6db3128"
            },
            {
              "example": "Mandag 10:00-12:00 Tirsdag 14:00-16:00",
              "name": "Åbningstid, telefon",
              "scope": "TEXT",
              "user_key": "Åbningstid Telefon",
              "uuid": "0836ffbf-3b3e-410f-8cbf-face7e6844ef"
            }
          ],
          "offset": 0,
          "total": 3
        }
      }
    '''
    orgid = str(orgid)
    class_details = map_query_args_to_class_details(util.get_query_args())

    return await get_classes_under_facet(
        orgid, facet, details=class_details,
        only_primary_uuid=only_primary_uuid,
        start=start, limit=limit
    )


def map_query_args_to_class_details(args):
    arg_map = {
        'full_name': ClassDetails.FULL_NAME,
        'top_level_facet': ClassDetails.TOP_LEVEL_FACET,
        'facet': ClassDetails.FACET
    }

    # If unknown args
    if not set(args) <= set(arg_map):
        exceptions.ErrorCodes.E_INVALID_INPUT(
            f'Invalid args: {set(args) - set(arg_map)}'
        )

    mapped = set(map(arg_map.get, args))

    return mapped


@router.get('/f/{facet}/')
async def get_all_classes(
    facet: str,
    start: Optional[int] = 0,
    limit: Optional[int] = 0,
    only_primary_uuid: Optional[bool] = None
):
    '''List classes available in the given facet.

    .. :quickref: Facet; Get

    :param string facet: One of the facet bvns/uuids.

    :queryparam int start: Index of first item for paging.
    :queryparam int limit: Maximum items.

    :>jsonarr string name: Human-readable name.
    :>jsonarr string uuid: Machine-friendly UUID.
    :>jsonarr string user_key: Short, unique key.
    :>jsonarr string example: An example value. In most cases the
        value is meant to be presented to the user as an aid.
    :>jsonarr string scope: A representation of the type of value, see
        the table below for details.

    :status 200: On success.
    :status 404: Whenever the facet isn't found.

    **Example Response**:

    .. sourcecode:: json

      {
        "name": "address_type",
        "path":
          "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address_type/",
        "user_key": "Adressetype",
        "uuid": "e337bab4-635f-49ce-aa31-b44047a43aa1",
        "data": {
          "items": [
            {
              "example": "http://www.korsbaek.dk/",
              "name": "Hjemmeside",
              "scope": "WWW",
              "user_key": "URL",
              "uuid": "160ecaed-50b0-4800-bebc-0d0289a4f624"
            },
            {
              "example": "<UUID>",
              "name": "Lokation",
              "scope": "DAR",
              "user_key": "AdresseLokation",
              "uuid": "031f93c3-6bab-462e-a998-87cad6db3128"
            },
            {
              "example": "Mandag 10:00-12:00 Tirsdag 14:00-16:00",
              "name": "Åbningstid, telefon",
              "scope": "TEXT",
              "user_key": "Åbningstid Telefon",
              "uuid": "0836ffbf-3b3e-410f-8cbf-face7e6844ef"
            }
          ],
          "offset": 0,
          "total": 3
        }
      }
    '''
    return await get_classes_under_facet(
        None, facet, only_primary_uuid=only_primary_uuid, start=start, limit=limit
    )


class ClassRequestHandler(handlers.RequestHandler):
    role_type = "class"

    def prepare_create(self, request: dict):
        valid_from = util.NEGATIVE_INFINITY
        valid_to = util.POSITIVE_INFINITY

        facet_bvn = request['facet']
        facetids = mora.async_util.async_to_sync(get_facetids)(facet_bvn)
        facet_uuid = one(facetids)

        mo_class = request['class_model']

        clazz = common.create_klasse_payload(
            valid_from=valid_from,
            valid_to=valid_to,
            facet_uuid=facet_uuid,
            org_uuid=mo_class.org_uuid,
            bvn=mo_class.user_key,
            title=mo_class.name,
            scope=mo_class.scope
        )

        self.payload = clazz
        self.uuid = mo_class.uuid or str(uuid4())

    def submit(self) -> str:
        c = lora.Connector()

        if self.request_type == mapping.RequestType.CREATE:
            self.result = mora.async_util.async_to_sync(c.klasse.create)(
                self.payload,
                self.uuid)
        else:
            self.result = mora.async_util.async_to_sync(c.klasse.update)(
                self.payload,
                self.uuid)

        return super().submit()


@router.post('/f/{facet}/')
def create_or_update_class(
    facet: str,
    class_model: MOClass,
):
    """Will create a new class if there's no UUID or it doesnt match an exiting class
    Will update an existing class if there's a matching UUID

    :param facet: One of the facet bvns/uuids.
    :param class_model: Pydantic BaseModel for a class
    """
    req = {'facet': facet, 'class_model': class_model}
    request = ClassRequestHandler(req, mapping.RequestType.CREATE)
    return request.submit()


@router.get('/f/{facet}/children')
async def get_all_classes_children(
    facet: str,
    start: Optional[int] = 0,
    limit: Optional[int] = 0,
    only_primary_uuid: Optional[bool] = None
):
    '''List classes available in the given facet.

    .. :quickref: Facet; Get

    :param string facet: One of the facet bvns/uuids.

    :queryparam int start: Index of first item for paging.
    :queryparam int limit: Maximum items.

    :>jsonarr string name: Human-readable name.
    :>jsonarr string uuid: Machine-friendly UUID.
    :>jsonarr string user_key: Short, unique key.
    :>jsonarr string example: An example value. In most cases the
        value is meant to be presented to the user as an aid.
    :>jsonarr string scope: A representation of the type of value, see
        the table below for details.

    :status 200: On success.
    :status 404: Whenever the facet isn't found.

    **Example Response**:

    .. sourcecode:: json

      {
        "name": "address_type",
        "path":
          "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/f/address_type/",
        "user_key": "Adressetype",
        "uuid": "e337bab4-635f-49ce-aa31-b44047a43aa1",
        "data": {
          "items": [
            {
              "example": "http://www.korsbaek.dk/",
              "name": "Hjemmeside",
              "scope": "WWW",
              "user_key": "URL",
              "uuid": "160ecaed-50b0-4800-bebc-0d0289a4f624"
            },
            {
              "example": "<UUID>",
              "name": "Lokation",
              "scope": "DAR",
              "user_key": "AdresseLokation",
              "uuid": "031f93c3-6bab-462e-a998-87cad6db3128"
            },
            {
              "example": "Mandag 10:00-12:00 Tirsdag 14:00-16:00",
              "name": "Åbningstid, telefon",
              "scope": "TEXT",
              "user_key": "Åbningstid Telefon",
              "uuid": "0836ffbf-3b3e-410f-8cbf-face7e6844ef"
            }
          ],
          "offset": 0,
          "total": 3
        }
      }

    '''

    c = common.get_connector()

    facetids = await get_facetids(facet)

    async def __get_one_class_helper(*args, **kwargs):
        """
        I'm an async lambda
        """
        return await get_one_class(*args, **kwargs, only_primary_uuid=only_primary_uuid)

    classes = (await c.klasse.paged_get(
        __get_one_class_helper,
        facet=facetids,
        ansvarlig=None,
        publiceret='Publiceret',
        start=start, limit=limit
    ))['items']
    classes = await gather(
        *[create_task(prepare_class_child(c, class_)) for class_ in classes]
    )

    return classes

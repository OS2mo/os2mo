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
import functools

import locale
import enum

import typing
import uuid
from functools import partial

import flask

from .. import common
from .. import exceptions
from .. import mapping
from .. import util

from .tree_helper import prepare_ancestor_tree


blueprint = flask.Blueprint('facet', __name__, static_url_path='',
                            url_prefix='/service')


@enum.unique
class ClassDetails(enum.Enum):
    # full class name
    FULL_NAME = 0
    # with child count
    NCHILDREN = 1
    TOP_LEVEL_FACET = 2
    FACET = 3


@blueprint.route('/c/ancestor-tree')
@util.restrictargs('at', 'uuid')
def get_class_ancestor_tree():
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
    classids = flask.request.args.getlist('uuid')

    return flask.jsonify(
        get_class_tree(c, classids, with_siblings=True)
    )


def get_class_tree(c, classids, with_siblings=False):
    """Return a tree, bounded by the given classid.

    The tree includes siblings of ancestors, with their child counts.
    """

    def get_class(classid):
        r = get_one_class(
            c, classid, cache[classid],
            details=(
                {ClassDetails.NCHILDREN}
                if with_siblings and classid not in children
                else None
            ),
        )
        if classid in children:
            r['children'] = get_classes(children[classid])
        return r

    def get_classes(classids):
        return sorted(
            map(get_class, classids),
            key=lambda u: locale.strxfrm(u[mapping.NAME]),
        )

    def get_children_args(uuid, parent_uuid, cache):
        return {"overordnetklasse": parent_uuid}

    root_uuids, children, cache = prepare_ancestor_tree(
        c.klasse,
        mapping.PARENT_CLASS_FIELD,
        classids,
        get_children_args,
        with_siblings=with_siblings
    )
    return get_classes(root for root in root_uuids)


@blueprint.route('/c/<uuid:classid>/')
@util.restrictargs('limit', 'start')
def get_class(classid: str):
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

    c = common.get_connector()
    return flask.jsonify(get_one_class(c, classid, None))


def prepare_class_child(c, entry):
    """Minimize and enrich JSON, by only returning relevant data."""
    return {
        'child_count': count_class_children(c, entry['uuid']),
        'name': entry['name'],
        'user_key': entry['user_key'],
        'uuid': entry['uuid']
    }


@blueprint.route('/c/<uuid:classid>/children')
@util.restrictargs('limit', 'start')
def get_all_class_children(classid: str):
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

    c = common.get_connector()
    fetch_class = partial(get_one_class, c)

    classes = fetch_class_children(c, classid)
    classes = map(lambda tup: fetch_class(*tup), classes)
    classes = map(partial(prepare_class_child, c), classes)

    return flask.jsonify(sorted(
        classes,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f['name']) if f.get('name') else '',
    ))


@blueprint.route('/o/<uuid:orgid>/f/')
@util.restrictargs()
def list_facets(orgid):
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

    c = common.get_connector()

    def transform(facet_tuple):
        facetid, facet = facet_tuple
        return get_one_facet(c, facetid, orgid, facet)

    response = c.facet.get_all(ansvarlig=orgid, publiceret='Publiceret')
    response = list(map(transform, response))
    return flask.jsonify(sorted(
        response,
        # use locale-aware sorting
        key=lambda f: locale.strxfrm(f['name']) if f.get('name') else '',
    ))


def get_one_facet(c, facetid, orgid=None, facet=None, data=None):
    """Fetch a facet and enrich it."""

    # Use given facet or fetch one, if none is given
    facet = facet or c.facet.get(facetid)
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
        response['path'] = (bvn and flask.url_for(
            'facet.get_classes', orgid=orgid, facet=bvn
        ))
    if data:
        response['data'] = data
    return response


def get_bulk_classes(c, uuids, details=None):
    """Fetch all classes defined by uuids.

    :queryparam uuids: A list of UUIDs of the classes.

    **Example Response**:

    .. sourcecode:: json

      {
         "71acc2cf-9a4f-465d-80b7-d6ba4d823ac5": {
             "uuid": "71acc2cf-9a4f-465d-80b7-d6ba4d823ac5"
             "name": "Industrigruppen",
             "user_key": "LO_3f_industri",
             "...": "..."
         },
         "...": "..."
      }

    """

    # TODO: Implement actual bulk lookup
    return {uuid: get_one_class(c, uuid, details=details) for uuid in uuids}


def fetch_class_children(c, parent_uuid):
    return list(
        c.klasse.get_all(publiceret='Publiceret', overordnetklasse=parent_uuid)
    )


def count_class_children(c, parent_uuid):
    """Find the number of children under the class given by uuid."""
    return len(fetch_class_children(c, parent_uuid))


def get_one_class(c, classid, clazz=None, details: typing.Set[ClassDetails] = None):
    if not details:
        details = set()

    only_primary_uuid = flask.request.args.get('only_primary_uuid')
    if only_primary_uuid:
        return {
            mapping.UUID: classid
        }

    if not clazz:
        clazz = c.klasse.get(classid)

        if not clazz:
            return None

    def get_attrs(clazz):
        return clazz['attributter']['klasseegenskaber'][0]

    attrs = get_attrs(clazz)
    parents = None

    def get_parent(clazz):
        """Find the parent UUID of the provided class object."""
        for parentid in mapping.PARENT_CLASS_FIELD.get_uuids(clazz):
            return parentid

    def get_parents(clazz):
        potential_parent = get_parent(clazz)
        if potential_parent is None:
            return [clazz]
        return [clazz] + get_parents(c.klasse.get(potential_parent))

    def get_full_name(clazz, parents):
        parents = get_parents(clazz)
        full_name = " - ".join(
            [get_attrs(clazz).get('titel') for clazz in reversed(parents)]
        )
        return full_name

    def get_facet_uuid(clazz):
        return clazz['relationer']['facet'][0]['uuid']

    def get_top_level_facet(parents):
        return get_one_facet(c, get_facet_uuid(parents[-1]), orgid=None)

    def get_facet(clazz):
        return get_one_facet(c, get_facet_uuid(clazz), orgid=None)

    response = {
        'uuid': classid,
        'name': attrs.get('titel'),
        'user_key': attrs.get('brugervendtnoegle'),
        'example': attrs.get('eksempel'),
        'scope': attrs.get('omfang'),
    }

    if ClassDetails.FULL_NAME in details:
        if not parents:
            parents = get_parents(clazz)
        response['full_name'] = get_full_name(clazz, parents)

    if ClassDetails.TOP_LEVEL_FACET in details:
        if not parents:
            parents = get_parents(clazz)
        response['top_level_facet'] = get_top_level_facet(parents)

    if ClassDetails.FACET in details:
        response['facet'] = get_facet(clazz)

    if ClassDetails.NCHILDREN in details:
        response['child_count'] = count_class_children(c, classid)

    return response

# Helper function for reading classes enriched with additional details
get_one_class_full = functools.partial(get_one_class, details={
    ClassDetails.FACET,
    ClassDetails.FULL_NAME,
    ClassDetails.TOP_LEVEL_FACET
})


def get_facetids(facet: str):

    c = common.get_connector()

    uuid, bvn = (facet, None) if util.is_uuid(facet) else (None, facet)

    facetids = c.facet(
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


def get_classes_under_facet(orgid: uuid.UUID, facet: str,
                            details: typing.Set[ClassDetails] = None):

    c = common.get_connector()

    start = int(flask.request.args.get('start') or 0)
    limit = int(flask.request.args.get('limit') or 0)

    facetids = get_facetids(facet)

    getter_fn = functools.partial(get_one_class, details=details)

    return flask.jsonify(
        facetids and get_one_facet(
            c,
            facetids[0],
            orgid,
            data=c.klasse.paged_get(
                getter_fn,
                facet=facetids,
                publiceret='Publiceret',
                start=start, limit=limit
            ),
        )
    )


@blueprint.route('/o/<uuid:orgid>/f/<facet>/')
@util.restrictargs('limit', 'start')
def get_classes(orgid: uuid.UUID, facet: str):
    '''List classes available in the given facet.

    .. :quickref: Facet; Get

    :param uuid orgid: Restrict search to this organisation.
    :param string facet: One of the facet names listed by
        :http:get:`/service/o/(uuid:orgid)/f/`

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
    class_details = map_query_args_to_class_details(flask.request.args)
    return get_classes_under_facet(orgid, facet, details=class_details)


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


@blueprint.route('/f/<facet>/')
@util.restrictargs('limit', 'start')
def get_all_classes(facet: str):
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
    return get_classes_under_facet(None, facet)


@blueprint.route('/f/<facet>/children')
@util.restrictargs('limit', 'start')
def get_all_classes_children(facet: str):
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

    start = int(flask.request.args.get('start') or 0)
    limit = int(flask.request.args.get('limit') or 0)

    facetids = get_facetids(facet)

    classes = c.klasse.paged_get(
        get_one_class,
        facet=facetids,
        ansvarlig=None,
        publiceret='Publiceret',
        start=start, limit=limit
    )['items']
    classes = map(partial(prepare_class_child, c), classes)

    return flask.jsonify(list(classes))

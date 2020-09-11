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

import locale
import enum
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
    # class only
    MINIMAL = 0

    # with child count
    NCHILDREN = 1


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
                ClassDetails.NCHILDREN
                if with_siblings and classid not in children
                else ClassDetails.MINIMAL
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


def get_bulk_classes(c, uuids):
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
    return {uuid: get_one_class(c, uuid) for uuid in uuids}


def fetch_class_children(c, parent_uuid):
    return list(
        c.klasse.get_all(publiceret='Publiceret', overordnetklasse=parent_uuid)
    )


def count_class_children(c, parent_uuid):
    """Find the number of children under the class given by uuid."""
    return len(fetch_class_children(c, parent_uuid))


def get_one_class(c, classid, clazz=None, details=ClassDetails.MINIMAL):

    only_primary_uuid = flask.request.args.get('only_primary_uuid')
    if only_primary_uuid:
        return {
            mapping.UUID: classid
        }

    if not clazz:
        clazz = c.klasse.get(classid)

        if not clazz:
            return None
            # exceptions.ErrorCodes.E_INVALID_INPUT(
            #     'no such class {!r}'.format(classid),
            # )

    def get_parent(clazz):
        """Find the parent UUID of the provided class object."""
        for parentid in mapping.PARENT_CLASS_FIELD.get_uuids(clazz):
            return parentid

    def get_parents(clazz):
        return_val = [clazz]
        potential_parent = get_parent(clazz)
        if potential_parent:
            return_val.extend(get_parents(c.klasse.get(potential_parent)))
        return return_val

    parents = get_parents(clazz)

    def get_attrs(clazz):
        return clazz['attributter']['klasseegenskaber'][0]

    def get_facet_uuid(clazz):
        return clazz['relationer']['facet'][0]['uuid']

    attrs = get_attrs(clazz)
    full_name = " - ".join([get_attrs(clazz).get('titel') for clazz in parents])

    response = {
        'uuid': classid,
        'full_name': full_name,
        'name': attrs.get('titel'),
        'user_key': attrs.get('brugervendtnoegle'),
        'example': attrs.get('eksempel'),
        'scope': attrs.get('omfang'),
        'top_level_facet': get_one_facet(c, get_facet_uuid(parents[-1]), orgid=None),
        'facet': get_one_facet(c, get_facet_uuid(clazz), orgid=None),
    }

    if details is ClassDetails.NCHILDREN:
        response['child_count'] = count_class_children(c, classid)
    elif details is ClassDetails.MINIMAL:
        pass  # already done
    else:
        raise AssertionError('enum is {}!?'.format(details))
    return response


def get_facetids(facet: str, extra_filters: dict = None):

    c = common.get_connector()

    uuid, bvn = (facet, None) if util.is_uuid(facet) else (None, facet)

    extra_filters = extra_filters or {}
    facetids = c.facet(
        uuid=uuid,
        bvn=bvn,
        publiceret='Publiceret',
        **extra_filters
    )

    if not facetids:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_NOT_FOUND,
            message="Facet {} not found.".format(facet)
        )

    assert len(facetids) <= 1, 'Facet is not unique'

    return facetids


def get_classes_under_facet(orgid: uuid.UUID, facet: str):

    c = common.get_connector()

    start = int(flask.request.args.get('start') or 0)
    limit = int(flask.request.args.get('limit') or 0)

    extra_filters = {'ansvarlig': orgid} if orgid else {}
    facetids = get_facetids(facet, extra_filters)

    return flask.jsonify(
        facetids and get_one_facet(
            c,
            facetids[0],
            orgid,
            data=c.klasse.paged_get(
                get_one_class,
                facet=facetids,
                publiceret='Publiceret',
                start=start, limit=limit,
                **extra_filters
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
    return get_classes_under_facet(orgid, facet)


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

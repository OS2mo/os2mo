#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import flask

from .. import util, lora
from ..service import handlers
from ..service.detail_reading import get_detail
from ..service.detail_writing import handle_requests

blueprint = flask.Blueprint('api', __name__, static_url_path='',
                            url_prefix='/service/api')


@blueprint.route('/<obj_type>', methods=['GET'])
@util.restrictargs('start', 'limit', 'only_primary_uuid')
def list_(obj_type):
    """
    List all objects of a given type

    .. :quickref: API; List objects
    """
    args = flask.request.args

    start = args.get('start')
    limit = args.get('limit')

    search_fields = {
        'start': start,
        'limit': limit,
    }
    search_fields = _filter_none_values(search_fields)

    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

    cls = handlers.get_handler_for_role_type(obj_type)

    if issubclass(cls, handlers.ReadingRequestHandler):
        return flask.jsonify(list(cls.get(c, search_fields)))

    return get_detail(c, obj_type, search_fields)


@blueprint.route('/<obj_type>/<obj_uuid>', methods=['GET'])
@util.restrictargs('start', 'limit', 'only_primary_uuid')
def get(obj_type, obj_uuid):
    """
    List specific object of a given type

    .. :quickref: API; Get object
    """
    args = flask.request.args

    start = args.get('start')
    limit = args.get('limit')

    search_fields = {
        'start': start,
        'limit': limit,
        'uuid': [obj_uuid],
    }
    search_fields = _filter_none_values(search_fields)

    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

    cls = handlers.get_handler_for_role_type(obj_type)

    if issubclass(cls, handlers.ReadingRequestHandler):
        return flask.jsonify(list(cls.get(c, search_fields)))

    return get_detail(c, obj_type, search_fields)


@blueprint.route('/<obj_type>/<obj_uuid>', methods=['PATCH'])
@util.restrictargs('force')
def patch(obj_type, obj_uuid):
    """
    Perform an update on an object

    .. :quickref: API; Update object
    """
    req = flask.request.get_json()

    edit_request = {
        'uuid': obj_uuid,
        'data': req,
        'type': obj_type,
    }

    return (
        flask.jsonify(
            handle_requests(edit_request, handlers.RequestType.EDIT)),
        200
    )


@blueprint.route('/<obj_type>', methods=['POST'])
@util.restrictargs('force')
def post(obj_type):
    """
    Create new object

    .. :quickref: API; Create object
    """
    req = flask.request.get_json()

    post_request = {
        'type': obj_type,
        **req,
    }

    return (
        flask.jsonify(
            handle_requests(post_request, handlers.RequestType.CREATE)),
        201
    )


@blueprint.route('/<obj_type>/<obj_uuid>', methods=['PUT'])
@util.restrictargs('force')
def put(obj_type, obj_uuid):
    """
    Import object

    .. :quickref: API; Import object
    """
    req = flask.request.get_json()

    put_request = {
        'type': obj_type,
        'uuid': obj_uuid,
        **req,
    }

    return (
        flask.jsonify(
            handle_requests(put_request, handlers.RequestType.CREATE)),
        201
    )


def _filter_none_values(dict: dict):
    return {k: v for k, v in dict.items() if v is not None}

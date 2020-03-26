# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import functools

import flask
import logging

from mora import conf_db, exceptions, util

blueprint = flask.Blueprint("read_only", __name__, static_url_path="", url_prefix="/")

logger = logging.getLogger(__name__)


@blueprint.route("/read_only/", methods=["PUT"])
@util.restrictargs()
def read_only():
    """Changes the read-only status for OS2mo

    .. :quickref: Read-only; Change status

    :statuscode 400: Invalid payload
    :statuscode 201: The termination succeeded.

    :<json boolean status: Whether read-only should be enabled or not.

    **Example Request**:

    .. sourcecode:: json

      {
        "status": true
      }
    """

    req = flask.request.get_json()
    if not req:
        return flask.jsonify("Payload missing from request"), 400

    status = req.get("status")
    if status is None:
        return flask.jsonify("'status' missing from payload"), 400

    configuration = {"org_units": {"read_only": status}}

    conf_db.set_configuration(
        configuration=configuration, unitid=None
    )

    return flask.jsonify({"success": True}), 201


def check_read_only(f):
    """
    Decorator for 'write' and 'edit' endpoints checking whether read-only mode is
    active, and whether a request originates from the UI
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if flask.request.headers.get('X-Client-Name') == 'OS2mo-UI':
            if conf_db.get_configuration(unitid=None).get('read_only'):
                return exceptions.ErrorCodes.E_READ_ONLY()

        return f(*args, **kwargs)

    wrapper.read_only = True

    return wrapper

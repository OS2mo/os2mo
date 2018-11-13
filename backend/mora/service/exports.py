#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import os

import flask

from .. import util
from .. import exceptions

blueprint = flask.Blueprint('exports', __name__, static_url_path='',
                            url_prefix='/service')


@blueprint.route('/exports/')
@util.restrictargs()
def list_export_files():
    """
    List the available exports

    .. :quickref: Exports; List

    :return: A list of available export files

    **Example Response**:

    .. sourcecode:: json

      [
        "export1.xlsx",
        "export2.xlsx"
      ]
    """
    export_dir = flask.current_app.config['QUERY_EXPORT_DIR']
    if not os.path.isdir(export_dir):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_DIR_NOT_FOUND,
        )
    dir_contents = os.listdir(export_dir)
    files = [
        file for file in dir_contents if
        os.path.isfile(os.path.join(export_dir, file))
    ]
    return flask.jsonify(files)


@blueprint.route('/exports/<string:file_name>')
@util.restrictargs()
def get_export_file(file_name: str):
    """
    Fetch a export file with a given name

    .. :quickref: Exports; Get

    :param string file_name: Name of the export file

    :return: The file corresponding to the given export file name
    """
    export_dir = flask.current_app.config['QUERY_EXPORT_DIR']
    if not os.path.isdir(export_dir):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_DIR_NOT_FOUND,
        )

    file_path = os.path.join(export_dir, file_name)
    if not os.path.isfile(file_path):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_NOT_FOUND,
            filename=file_name
        )

    return flask.send_file(file_path)

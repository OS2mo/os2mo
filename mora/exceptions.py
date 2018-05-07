#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import typing

import flask
import werkzeug.exceptions

from .errors import Error
from . import util


class BaseError(werkzeug.exceptions.HTTPException):
    key = Error.E99999
    cause = 'unknown'
    code = 500

    def __init__(self,
                 key: typing.Optional[Error]=None,
                 **context) -> None:
        if key:
            self.key = key

        super().__init__(self.key.value)

        self.context = context

    def get_headers(self, environ=None):
        return [('Content-Type', flask.current_app.config['JSONIFY_MIMETYPE'])]

    def get_body(self, environ=None):
        return flask.json.dumps(
            {
                'error': True,
                'description': self.key.value,
                'cause': self.cause,
                'status': self.code,
                'key': self.key.name,

                **self.context,
            },
            indent=2,
        )


class ValidationError(BaseError):
    key = Error.E90000
    cause = 'validation'
    code = 400


class NotFoundError(BaseError):
    key = Error.E90003
    cause = 'not-found'
    code = 404


class UnauthorizedError(BaseError):
    key = Error.E90001
    cause = 'unauthorized'
    code = 401

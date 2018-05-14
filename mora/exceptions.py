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

from .errorcodes import ErrorCodes
from . import util


class BaseError(werkzeug.exceptions.HTTPException):
    key = ErrorCodes.E_UNKNOWN
    cause = 'unknown'
    code = 500

    def __init__(self,
                 key: typing.Optional[ErrorCodes]=None,
                 **context) -> None:
        if key:
            self.key = key

        code, description = self.key.value
        self.code = code
        self.context = context

        super().__init__(description)

    def get_headers(self, environ=None):
        return [('Content-Type', flask.current_app.config['JSONIFY_MIMETYPE'])]

    def get_body(self, environ=None):
        code, description = self.key.value
        return flask.json.dumps(
            {
                'error': True,
                'description': description,
                'cause': self.cause,
                'status': code,
                'key': self.key.name,

                **self.context,
            },
            indent=2,
        )


class ValidationError(BaseError):
    key = ErrorCodes.E_INVALID_INPUT
    cause = 'validation'


class NotFoundError(BaseError):
    key = ErrorCodes.E_NOT_FOUND
    cause = 'not-found'


class UnauthorizedError(BaseError):
    key = ErrorCodes.E_UNAUTHORIZED
    cause = 'unauthorized'

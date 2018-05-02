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

from . import util


class BaseError(werkzeug.exceptions.HTTPException):
    description = 'An unknown error occurred.'
    cause = 'unknown'
    code = 500

    def __init__(self,
                 description: typing.Optional[str]=None,
                 **context) -> None:
        super().__init__(description or type(self).description)

        self.context = context

    def get_headers(self, environ=None):
        return [('Content-Type', flask.current_app.config['JSONIFY_MIMETYPE'])]

    def get_body(self, environ=None):
        return flask.json.dumps(
            {
                'error': True,
                'description': self.description,
                'cause': self.cause,
                'status': self.code,

                **self.context,
            },
            indent=2,
        )


class ValidationError(BaseError):
    description = 'Invalid input.'
    cause = 'validation'
    code = 400


class NotFoundError(BaseError):
    description = 'Not found.'
    cause = 'not-found'
    code = 404


class UnauthorizedError(BaseError):
    description = 'Access denied.'
    cause = 'unauthorized'
    code = 401

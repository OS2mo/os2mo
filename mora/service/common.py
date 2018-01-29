#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import collections
from enum import Enum

import collections
import functools

import flask
import iso8601

from .. import lora

PropTuple = collections.namedtuple(
    'PropTuple',
    [
        'path',
        'type',
        'filter_fn',
    ]
)


class PropTypes(Enum):
    ZERO_TO_ONE = 0,
    ZERO_TO_MANY = 1,
    ADAPTED_ZERO_TO_MANY = 2,


def get_connector():
    args = flask.request.args

    loraparams = dict()

    if args.get('at'):
        loraparams['effective_date'] = iso8601.parse_date(args['at'])

    if args.get('validity'):
        loraparams['validity'] = args['validity']

    return lora.Connector(**loraparams)


class cache(collections.defaultdict):
    '''combination of functools.partial & defaultdict into one'''

    def __init__(self, func, *args, **kwargs):
        super().__init__(functools.partial(func, *args, **kwargs))

    def __missing__(self, key):
        v = self[key] = self.default_factory(key)
        return v

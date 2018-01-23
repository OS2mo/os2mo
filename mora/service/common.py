#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import flask
import iso8601

from .. import lora


def get_connector():
    args = flask.request.args

    loraparams = dict()

    if args.get('at'):
        loraparams['effective_date'] = iso8601.parse_date(args['at'])

    return lora.Connector(**loraparams)

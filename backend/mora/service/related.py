#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Related Units
-------------

This section describes how to interact with related units.

'''

from . import handlers
from .. import common
from .. import exceptions
from .. import lora
from .. import mapping
from .. import util
from .. import validator


class RelatedUnitRequestHandler(handlers.OrgFunkRequestHandler):
    '''This is a dummy handler that exists to enable reading related units.

    Eventually, we'll do that in the handlers, but for now we use
    their _existence_ to allow reading.

    '''
    __slots__ = ()

    role_type = 'related_unit'
    function_key = mapping.RELATED_UNIT_KEY

    def prepare_create(self, req: dict):
        raise NotImplementedError

    def prepare_edit(self, req: dict):
        raise NotImplementedError

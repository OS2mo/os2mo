
#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import util
from mora.triggers import Trigger
from mora.mapping import (
    ON_AFTER,
    ORG_UNIT
)
from mora.service.handlers import RequestType


class Tests(util.LoRATestCase):

    def test_orgunit_trigger_after_delete(self):
        called = []

        @Trigger.on(ORG_UNIT, RequestType.TERMINATE, ON_AFTER)
        def del_trigger(trigger_dict):
            called.append(trigger_dict["uuid"])

        self.load_sample_structures()
        uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

        url = '/service/ou/{}/terminate'.format(uuid)
        self.assertRequest(
            url,
            json={"validity": {"to": "2017-01-02"}}
        )
        # trigger is called ok
        self.assertEqual([uuid], called)

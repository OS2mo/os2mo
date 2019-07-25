#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import util
import freezegun
from mora.triggers import Trigger
from mora.mapping import ORG_UNIT
from mora.service.handlers import RequestType


@freezegun.freeze_time('2017-01-01')
class Tests(util.LoRATestCase):
    uuid = 'b688513d-11f7-4efc-b679-ab082a2055d0'

    def setUp(self):
        super().setUp()
        self.load_sample_structures()
        self.trigger_called = False

    def test_orgunit_trigger_before_delete(self):

        @Trigger.on(ORG_UNIT, RequestType.TERMINATE, Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'uuid': self.uuid,
                'event_type': Trigger.Event.ON_BEFORE,
                'request': {'validity': {'to': '2018-01-01'}},
                'request_type': RequestType.TERMINATE,
                'role_type': ORG_UNIT,
            }, trigger_dict)

        url = '/service/ou/{}/terminate'.format(self.uuid)
        self.assertRequest(
            url,
            json={"validity": {"to": "2018-01-01"}}
        )
        # assert trigger is called
        self.assertTrue(self.trigger_called)

    def test_orgunit_trigger_after_delete(self):

        @Trigger.on(ORG_UNIT, RequestType.TERMINATE, Trigger.Event.ON_AFTER)
        def trigger(trigger_dict):
            self.trigger_called = True
            trigger_dict.pop("result")
            self.assertEqual({
                'uuid': self.uuid,
                'event_type': Trigger.Event.ON_AFTER,
                'request': {'validity': {'to': '2018-01-01'}},
                'request_type': RequestType.TERMINATE,
                'role_type': ORG_UNIT,
            }, trigger_dict)

        url = '/service/ou/{}/terminate'.format(self.uuid)
        self.assertRequest(
            url,
            json={"validity": {"to": "2018-01-01"}}
        )
        self.assertTrue(self.trigger_called)

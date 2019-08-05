
#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import freezegun
from . import util
from mora.triggers import Trigger
from mora.service.handlers import (
    RequestType,
    RequestHandler,
)
from mora.mapping import ORG_UNIT


class MockHandler(RequestHandler):
    role_type = "mock"

    def prepare_edit(self, req):
        self.uuid = "edit"

    def prepare_create(self, req):
        self.uuid = "create"

    def prepare_terminate(self, req):
        self.uuid = "terminate"

    def submit(self):
        super().submit(result="okidoki")


class Tests(util.TestCase):
    maxDiff = None

    def tearDown(self):
        del Trigger.registry["mock"]
        super().tearDown()

    def setUp(self):
        if "mock" in Trigger.registry:
            self.fail("No role_type named 'mock' allowed in "
                      "Trigger.registry outside this test")
        super().setUp()

    def test_handler_trigger_before_edit(self):
        @Trigger.on("mock", RequestType.EDIT, Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_BEFORE,
                'request': {},
                'request_type': RequestType.EDIT,
                'role_type': 'mock',
                'uuid': 'edit'
            }, trigger_dict)
        MockHandler({}, RequestType.EDIT)
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_after_edit(self):
        @Trigger.on("mock", RequestType.EDIT, Trigger.Event.ON_AFTER)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_AFTER,
                'request': {},
                'request_type': RequestType.EDIT,
                'role_type': 'mock',
                'uuid': 'edit',
                'result': 'okidoki'
            }, trigger_dict)
        MockHandler({}, RequestType.EDIT).submit()
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_before_create(self):
        @Trigger.on("mock", RequestType.CREATE, Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_BEFORE,
                'request': {},
                'request_type': RequestType.CREATE,
                'role_type': 'mock',
                'uuid': 'create'
            }, trigger_dict)
        MockHandler({}, RequestType.CREATE)
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_after_create(self):
        @Trigger.on("mock", RequestType.CREATE, Trigger.Event.ON_AFTER)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_AFTER,
                'request': {},
                'request_type': RequestType.CREATE,
                'uuid': 'create',
                'role_type': 'mock',
                'result': 'okidoki'
            }, trigger_dict)
        MockHandler({}, RequestType.CREATE).submit()
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_before_terminate(self):
        @Trigger.on("mock", RequestType.TERMINATE, Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_BEFORE,
                'request': {},
                'request_type': RequestType.TERMINATE,
                'role_type': 'mock',
                'uuid': 'terminate'
            }, trigger_dict)
        MockHandler({}, RequestType.TERMINATE)
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_after_terminate(self):
        @Trigger.on("mock", RequestType.TERMINATE, Trigger.Event.ON_AFTER)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_AFTER,
                'request': {},
                'request_type': RequestType.TERMINATE,
                'uuid': 'terminate',
                'role_type': 'mock',
                'result': 'okidoki'
            }, trigger_dict)
        MockHandler({}, RequestType.TERMINATE).submit()
        self.assertTrue(self.trigger_called)


@freezegun.freeze_time('2016-01-01')
class TriggerlessTests(util.LoRATestCase):
    """ Trigger functionality (and there by also amqp as that is triggered)
    can be disabled by the 'triggerless' flag
    This test is supposed to test/show the the difference
    """

    def trigger(self, trigger_dict):
        self.trigger_called = True

    def setUp(self):
        super().setUp()
        self.trigger_called = False
        self.trigger_before = Trigger.on(
            ORG_UNIT, RequestType.TERMINATE, Trigger.Event.ON_AFTER
        )(self.trigger)

    def tearDown(self):
        super().tearDown()
        del self.trigger_before

    def test_flag_on(self):
        self.load_sample_structures()
        unitid = "85715fc7-925d-401b-822d-467eb4b163b6"
        payload = {"validity": {"to": "2016-10-21"}}
        self.assertRequestResponse(
            '/service/ou/{}/terminate?triggerless=1'.format(unitid),
            unitid,
            json=payload,
            amqp_topics={},
        )
        self.assertFalse(self.trigger_called)

    def test_flag_off(self):
        self.load_sample_structures()
        unitid = "85715fc7-925d-401b-822d-467eb4b163b6"
        payload = {"validity": {"to": "2016-10-21"}}
        self.assertRequestResponse(
            '/service/ou/{}/terminate'.format(unitid),
            unitid,
            json=payload,
            amqp_topics={'org_unit.org_unit.delete': 1},
        )
        self.assertTrue(self.trigger_called)


#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import util
from mora.triggers import Trigger
from mora.service.handlers import (
    RequestType,
    RequestHandler,
)


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

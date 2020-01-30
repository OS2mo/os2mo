# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import freezegun
from . import util
from mora.triggers import Trigger
from mora.service.handlers import (
    RequestHandler
)
from mora.exceptions import HTTPException


class MockHandler(RequestHandler):
    role_type = "mock"
    result = "okidoki"

    def prepare_edit(self, req):
        self.uuid = "edit"

    def prepare_create(self, req):
        self.uuid = "create"

    def prepare_terminate(self, req):
        self.uuid = "terminate"

    def submit(self):
        super().submit()


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

    def test_handler_trigger_any_exception(self):
        @Trigger.on("mock", Trigger.RequestType.EDIT, Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            raise Exception("Bummer")
        with self.assertRaisesRegex(HTTPException, "400 Bad Request: Bummer"):
            MockHandler({}, Trigger.RequestType.EDIT)
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_own_error(self):
        @Trigger.on("mock", Trigger.RequestType.EDIT, Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            raise Trigger.Error("Bummer", stage="final")
        with self.assertRaises(HTTPException) as ctxt:
            MockHandler({}, Trigger.RequestType.EDIT)
        self.assertEqual({
            'error': True,
            'error_key': 'E_INTEGRATION_ERROR',
            'stage': 'final',
            'description': 'Bummer',
            'status': 400
        }, ctxt.exception.body)
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_before_edit(self):
        @Trigger.on("mock", Trigger.RequestType.EDIT, Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_BEFORE,
                'request': {},
                'request_type': Trigger.RequestType.EDIT,
                'role_type': 'mock',
                'uuid': 'edit'
            }, trigger_dict)
        MockHandler({}, Trigger.RequestType.EDIT)
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_after_edit(self):
        @Trigger.on("mock", Trigger.RequestType.EDIT, Trigger.Event.ON_AFTER)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_AFTER,
                'request': {},
                'request_type': Trigger.RequestType.EDIT,
                'role_type': 'mock',
                'uuid': 'edit',
                'result': 'okidoki'
            }, trigger_dict)
        MockHandler({}, Trigger.RequestType.EDIT).submit()
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_before_create(self):
        @Trigger.on("mock", Trigger.RequestType.CREATE,
                    Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_BEFORE,
                'request': {},
                'request_type': Trigger.RequestType.CREATE,
                'role_type': 'mock',
                'uuid': 'create'
            }, trigger_dict)
        MockHandler({}, Trigger.RequestType.CREATE)
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_after_create(self):
        @Trigger.on("mock", Trigger.RequestType.CREATE, Trigger.Event.ON_AFTER)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_AFTER,
                'request': {},
                'request_type': Trigger.RequestType.CREATE,
                'uuid': 'create',
                'role_type': 'mock',
                'result': 'okidoki'
            }, trigger_dict)
        MockHandler({}, Trigger.RequestType.CREATE).submit()
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_before_terminate(self):
        @Trigger.on("mock", Trigger.RequestType.TERMINATE,
                    Trigger.Event.ON_BEFORE)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_BEFORE,
                'request': {},
                'request_type': Trigger.RequestType.TERMINATE,
                'role_type': 'mock',
                'uuid': 'terminate'
            }, trigger_dict)
        MockHandler({}, Trigger.RequestType.TERMINATE)
        self.assertTrue(self.trigger_called)

    def test_handler_trigger_after_terminate(self):
        @Trigger.on("mock", Trigger.RequestType.TERMINATE,
                    Trigger.Event.ON_AFTER)
        def trigger(trigger_dict):
            self.trigger_called = True
            self.assertEqual({
                'event_type': Trigger.Event.ON_AFTER,
                'request': {},
                'request_type': Trigger.RequestType.TERMINATE,
                'uuid': 'terminate',
                'role_type': 'mock',
                'result': 'okidoki'
            }, trigger_dict)
        MockHandler({}, Trigger.RequestType.TERMINATE).submit()
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
            Trigger.ORG_UNIT,
            Trigger.RequestType.TERMINATE,
            Trigger.Event.ON_AFTER
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

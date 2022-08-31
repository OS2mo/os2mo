# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import freezegun
import pytest

import tests.cases
from mora.exceptions import HTTPException
from mora.mapping import EventType
from mora.mapping import RequestType
from mora.service.handlers import RequestHandler
from mora.triggers import Trigger
from tests.util import sample_structures_cls_fixture


class MockHandler(RequestHandler):
    role_type = "mock"
    result = "okidoki"

    async def prepare_edit(self, req):
        self.uuid = "edit"

    async def prepare_create(self, req):
        self.uuid = "create"

    async def prepare_terminate(self, req):
        self.uuid = "terminate"

    async def submit(self):
        await super().submit()


@sample_structures_cls_fixture
@freezegun.freeze_time("2016-01-01")
class TriggerlessTests(tests.cases.LoRATestCase):
    """Trigger functionality (and there by also amqp as that is triggered)
    can be disabled by the 'triggerless' flag
    This test is supposed to test/show the the difference
    """

    async def trigger(self, trigger_dict):
        self.trigger_called = True

    def setUp(self):
        super().setUp()
        self.trigger_called = False
        self.trigger_before = Trigger.on(
            "org_unit", RequestType.TERMINATE, EventType.ON_AFTER
        )(self.trigger)

    def tearDown(self):
        super().tearDown()
        del self.trigger_before

    def test_flag_on(self):
        unitid = "85715fc7-925d-401b-822d-467eb4b163b6"
        payload = {"validity": {"to": "2016-10-21"}}
        self.assertRequestResponse(
            "/service/ou/{}/terminate?triggerless=1".format(unitid),
            unitid,
            json=payload,
            amqp_topics={},
        )
        self.assertFalse(self.trigger_called)

    def test_flag_off(self):
        unitid = "85715fc7-925d-401b-822d-467eb4b163b6"
        payload = {"validity": {"to": "2016-10-21"}}
        self.assertRequestResponse(
            "/service/ou/{}/terminate".format(unitid),
            unitid,
            json=payload,
            amqp_topics={"org_unit.org_unit.delete": 1},
        )
        self.assertTrue(self.trigger_called)


async def test_handler_trigger_any_exception():
    @Trigger.on("mock", RequestType.EDIT, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called = True
        if trigger_called:
            raise Exception("Bummer")

    with pytest.raises(HTTPException) as err:
        await MockHandler.construct({}, RequestType.EDIT)
    assert err.value.detail == {
        "description": "Bummer",
        "error": True,
        "error_key": "E_INTEGRATION_ERROR",
        "status": 400,
    }


async def test_handler_trigger_own_error():
    @Trigger.on("mock", RequestType.EDIT, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called = True
        if trigger_called:
            raise Trigger.Error("Bummer", stage="final")

    with pytest.raises(HTTPException) as ctxt:
        await MockHandler.construct({}, RequestType.EDIT)
    assert ctxt.value.detail == {
        "error": True,
        "error_key": "E_INTEGRATION_ERROR",
        "stage": "final",
        "description": "Bummer",
        "status": 400,
    }


async def test_handler_trigger_before_edit():
    @Trigger.on("mock", RequestType.EDIT, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called = True
        if trigger_called:
            assert trigger_dict == {
                "event_type": EventType.ON_BEFORE,
                "request": {},
                "request_type": RequestType.EDIT,
                "role_type": "mock",
                "uuid": "edit",
            }

    await MockHandler.construct({}, RequestType.EDIT)


async def test_handler_trigger_after_edit():
    @Trigger.on("mock", RequestType.EDIT, EventType.ON_AFTER)
    async def trigger(trigger_dict):
        trigger_called = True
        if trigger_called:
            assert trigger_dict == {
                "event_type": EventType.ON_AFTER,
                "request": {},
                "request_type": RequestType.EDIT,
                "role_type": "mock",
                "uuid": "edit",
                "result": "okidoki",
            }

    await (await MockHandler.construct({}, RequestType.EDIT)).submit()


async def test_handler_trigger_before_create():
    @Trigger.on("mock", RequestType.CREATE, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called = True
        if trigger_called:
            assert trigger_dict == {
                "event_type": EventType.ON_BEFORE,
                "request": {},
                "request_type": RequestType.CREATE,
                "role_type": "mock",
                "uuid": "create",
            }

    await MockHandler.construct({}, RequestType.CREATE)


async def test_handler_trigger_after_create():
    @Trigger.on("mock", RequestType.CREATE, EventType.ON_AFTER)
    async def trigger(trigger_dict):
        trigger_called = True
        if trigger_called:
            assert trigger_dict == {
                "event_type": EventType.ON_AFTER,
                "request": {},
                "request_type": RequestType.CREATE,
                "uuid": "create",
                "role_type": "mock",
                "result": "okidoki",
            }

    await (await MockHandler.construct({}, RequestType.CREATE)).submit()


async def test_handler_trigger_before_terminate():
    @Trigger.on("mock", RequestType.TERMINATE, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called = True
        if trigger_called:
            assert trigger_dict == {
                "event_type": EventType.ON_BEFORE,
                "request": {},
                "request_type": RequestType.TERMINATE,
                "role_type": "mock",
                "uuid": "terminate",
            }

    await MockHandler.construct({}, RequestType.TERMINATE)


async def test_handler_trigger_after_terminate():
    @Trigger.on("mock", RequestType.TERMINATE, EventType.ON_AFTER)
    async def trigger(trigger_dict):
        trigger_called = True
        if trigger_called:
            assert trigger_dict == {
                "event_type": EventType.ON_AFTER,
                "request": {},
                "request_type": RequestType.TERMINATE,
                "uuid": "terminate",
                "role_type": "mock",
                "result": "okidoki",
            }

    await (await MockHandler.construct({}, RequestType.TERMINATE)).submit()

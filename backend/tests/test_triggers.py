# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from mora.exceptions import HTTPException
from mora.mapping import EventType
from mora.mapping import RequestType
from mora.service.handlers import RequestHandler
from mora.triggers import Trigger

from tests.conftest import YieldFixture


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


@pytest.fixture
def teardown_registry() -> YieldFixture[None]:
    assert "mock" not in Trigger.registry
    yield
    del Trigger.registry["mock"]


@pytest.mark.usefixtures("teardown_registry")
async def test_handler_trigger_any_exception() -> None:
    trigger_called = {"entry": False}

    @Trigger.on("mock", RequestType.EDIT, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called["entry"] = True
        raise Exception("Bummer")

    with pytest.raises(HTTPException) as err:
        await MockHandler.construct({}, RequestType.EDIT)

    assert {
        "description": "Bummer",
        "error": True,
        "error_key": "E_INTEGRATION_ERROR",
        "status": 400,
    } == err.value.detail
    assert trigger_called["entry"]


@pytest.mark.usefixtures("teardown_registry")
async def test_handler_trigger_own_error() -> None:
    trigger_called = {"entry": False}

    @Trigger.on("mock", RequestType.EDIT, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called["entry"] = True
        raise Trigger.Error("Bummer", stage="final")

    with pytest.raises(HTTPException) as ctxt:
        await MockHandler.construct({}, RequestType.EDIT)

    assert {
        "error": True,
        "error_key": "E_INTEGRATION_ERROR",
        "stage": "final",
        "description": "Bummer",
        "status": 400,
    } == ctxt.value.detail
    assert trigger_called["entry"]


@pytest.mark.usefixtures("teardown_registry")
async def test_handler_trigger_before_edit() -> None:
    trigger_called = {"entry": False}

    @Trigger.on("mock", RequestType.EDIT, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called["entry"] = True
        assert {
            "event_type": EventType.ON_BEFORE,
            "request": {},
            "request_type": RequestType.EDIT,
            "role_type": "mock",
            "uuid": "edit",
        } == trigger_dict

    await MockHandler.construct({}, RequestType.EDIT)
    assert trigger_called["entry"]


@pytest.mark.usefixtures("teardown_registry")
async def test_handler_trigger_after_edit() -> None:
    trigger_called = {"entry": False}

    @Trigger.on("mock", RequestType.EDIT, EventType.ON_AFTER)
    async def trigger(trigger_dict):
        trigger_called["entry"] = True
        assert {
            "event_type": EventType.ON_AFTER,
            "request": {},
            "request_type": RequestType.EDIT,
            "role_type": "mock",
            "uuid": "edit",
            "result": "okidoki",
        } == trigger_dict

    await (await MockHandler.construct({}, RequestType.EDIT)).submit()
    assert trigger_called["entry"]


@pytest.mark.usefixtures("teardown_registry")
async def test_handler_trigger_before_create() -> None:
    trigger_called = {"entry": False}

    @Trigger.on("mock", RequestType.CREATE, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called["entry"] = True
        assert {
            "event_type": EventType.ON_BEFORE,
            "request": {},
            "request_type": RequestType.CREATE,
            "role_type": "mock",
            "uuid": "create",
        } == trigger_dict

    await MockHandler.construct({}, RequestType.CREATE)
    assert trigger_called["entry"]


@pytest.mark.usefixtures("teardown_registry")
async def test_handler_trigger_after_create() -> None:
    trigger_called = {"entry": False}

    @Trigger.on("mock", RequestType.CREATE, EventType.ON_AFTER)
    async def trigger(trigger_dict):
        trigger_called["entry"] = True
        assert {
            "event_type": EventType.ON_AFTER,
            "request": {},
            "request_type": RequestType.CREATE,
            "uuid": "create",
            "role_type": "mock",
            "result": "okidoki",
        } == trigger_dict

    await (await MockHandler.construct({}, RequestType.CREATE)).submit()
    assert trigger_called["entry"]


@pytest.mark.usefixtures("teardown_registry")
async def test_handler_trigger_before_terminate() -> None:
    trigger_called = {"entry": False}

    @Trigger.on("mock", RequestType.TERMINATE, EventType.ON_BEFORE)
    async def trigger(trigger_dict):
        trigger_called["entry"] = True
        assert {
            "event_type": EventType.ON_BEFORE,
            "request": {},
            "request_type": RequestType.TERMINATE,
            "role_type": "mock",
            "uuid": "terminate",
        } == trigger_dict

    await MockHandler.construct({}, RequestType.TERMINATE)
    assert trigger_called["entry"]


@pytest.mark.usefixtures("teardown_registry")
async def test_handler_trigger_after_terminate() -> None:
    trigger_called = {"entry": False}

    @Trigger.on("mock", RequestType.TERMINATE, EventType.ON_AFTER)
    async def trigger(trigger_dict):
        trigger_called["entry"] = True
        assert {
            "event_type": EventType.ON_AFTER,
            "request": {},
            "request_type": RequestType.TERMINATE,
            "uuid": "terminate",
            "role_type": "mock",
            "result": "okidoki",
        } == trigger_dict

    await (await MockHandler.construct({}, RequestType.TERMINATE)).submit()
    assert trigger_called["entry"]

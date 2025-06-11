# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mo_ldap_import_export import depends


async def test_exit_stack_dependency() -> None:
    app = FastAPI()
    state_dict = {}

    @contextmanager
    def state_dict_writer() -> Iterator[None]:
        state_dict["startup"] = True
        yield
        state_dict["cleanup"] = True

    @app.get("/")
    async def handler(
        exit_stack: depends.ExitStack,
    ) -> None:
        assert state_dict == {}
        exit_stack.enter_context(state_dict_writer())
        assert state_dict == {"startup": True}

    client = TestClient(app)
    assert state_dict == {}
    client.get("/")
    assert state_dict == {"startup": True, "cleanup": True}

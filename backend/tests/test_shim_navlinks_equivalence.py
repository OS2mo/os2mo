# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import contextlib
import json
from typing import Any

import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from mora import config
from tests.util import override_config


# Old get_navlinks implementation
def get_navlinks():
    navlinks = config.get_settings().navlinks
    if not navlinks:
        navlinks = [{}]
    return navlinks


@contextlib.contextmanager
def override_settings(*args: Any, **kwargs: Any) -> None:
    with override_config(config.Settings(*args, **kwargs)):
        yield


@pytest.mark.equivalence
@pytest.mark.parametrize(
    "navlinks",
    [
        [],
        [{"href": "http://example.com", "text": "Example"}],
        [
            {"href": "http://example.com", "text": "Example1"},
            {"href": "http://example.org", "text": "Example2"},
        ],
    ],
)
async def test_navlinks_equivalence(
    service_client: TestClient, navlinks: dict[str, str]
) -> None:
    with override_settings(navlinks=navlinks):
        old_navlinks = get_navlinks()
        old_navlinks_str = json.dumps(jsonable_encoder(old_navlinks))

        response = service_client.get("/service/navlinks")
        new_navlinks = response.json()
        new_navlinks_str = json.dumps(jsonable_encoder(new_navlinks))

        assert old_navlinks_str == new_navlinks_str

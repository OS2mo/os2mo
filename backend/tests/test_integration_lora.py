# SPDX-FileCopyrightText: 2017-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio

import pytest
from aioresponses import CallbackResult
from yarl import URL

from mora.lora import Connector

a1_b1 = {"a": 1, "b": 1}
a1_b2 = {"a": 1, "b": 2}
a2_b1 = {"a": 2, "b": 1}
a2_b2 = {"a": 2, "b": 2}


@pytest.fixture
def mock_organisationenhed_requests(aioresponses):
    def callback(url, json, **kwargs):
        if json.get("list") is not None:
            payload = {
                "results": [
                    [
                        {"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"},
                    ]
                ],
            }
        else:
            payload = {
                "results": [
                    [
                        a1_b1,
                        a1_b2,
                        a2_b1,
                        a2_b2,
                    ]
                ]
            }
        return CallbackResult(status=200, payload=payload)

    url = URL("http://mox/organisation/organisationenhed")
    aioresponses.get(
        url,
        callback=callback,
        repeat=True,
    )
    return lambda: [
        r.kwargs["json"]
        for r in aioresponses.requests.get(("GET", url))
        if r.kwargs.get("json", {}).get("list")
    ]


class TestLoraDataLoader:
    @pytest.mark.asyncio
    async def test_load_single_param(self, mock_organisationenhed_requests):
        c = Connector()
        load_a1, load_a2, load_a1_again = await asyncio.gather(
            c.organisationenhed.load(a=1),
            c.organisationenhed.load(a=2),
            c.organisationenhed.load(a=1),
        )

        call_args = mock_organisationenhed_requests()[0]
        assert call_args["a"] == [1, 2]
        assert load_a1 == load_a1_again == [a1_b1, a1_b2]
        assert load_a2 == [a2_b1, a2_b2]

    @pytest.mark.asyncio
    async def test_load_merge_params(self, mock_organisationenhed_requests):
        c = Connector()
        load_a1, load_b1, load_a2, load_b2 = await asyncio.gather(
            c.organisationenhed.load(a=1),  # call 0
            c.organisationenhed.load(b=1),  # call 1
            c.organisationenhed.load(a=2),  # call 0
            c.organisationenhed.load(b=2),  # call 1
        )

        call_args = mock_organisationenhed_requests()[0]
        assert call_args["a"] == [1, 2]
        assert load_a1 == [a1_b1, a1_b2]
        assert load_a2 == [a2_b1, a2_b2]

        call_args = mock_organisationenhed_requests()[1]
        assert call_args["b"] == [1, 2]
        assert load_b1 == [a1_b1, a2_b1]
        assert load_b2 == [a1_b2, a2_b2]

    @pytest.mark.asyncio
    async def test_load_multi_params(self, mock_organisationenhed_requests):
        c = Connector()
        load_a1, load_a1_b1 = await asyncio.gather(
            c.organisationenhed.load(a=1),       # call 0
            c.organisationenhed.load(a=1, b=1),  # call 1
        )

        call_args = mock_organisationenhed_requests()[0]
        assert call_args["a"] == [1]
        assert load_a1 == [a1_b1, a1_b2]

        call_args = mock_organisationenhed_requests()[1]
        assert call_args["a"] == [1]
        assert call_args["b"] == [1]
        assert load_a1_b1 == [a1_b1]

    @pytest.mark.asyncio
    async def test_load_merge_multi_params(self, mock_organisationenhed_requests):
        c = Connector()
        load_a1_b1, load_a1_b2, load_b1, load_a1, load_a2_b1 = await asyncio.gather(
            c.organisationenhed.load(a=1, b=1),  # call 0
            c.organisationenhed.load(a=1, b=2),  # call 0
            c.organisationenhed.load(b=1),       # call 1
            c.organisationenhed.load(a=1),       # call 2
            c.organisationenhed.load(a=2, b=1),  # call 0
        )

        call_args = mock_organisationenhed_requests()[0]
        assert call_args["a"] == [1, 2]
        assert call_args["b"] == [1, 2]
        assert load_a1_b1 == [a1_b1]
        assert load_a1_b2 == [a1_b2]
        assert load_a2_b1 == [a2_b1]

        call_args = mock_organisationenhed_requests()[1]
        assert call_args["b"] == [1]
        assert load_b1 == [a1_b1, a2_b1]

        call_args = mock_organisationenhed_requests()[2]
        assert call_args["a"] == [1]
        assert load_a1 == [a1_b1, a1_b2]

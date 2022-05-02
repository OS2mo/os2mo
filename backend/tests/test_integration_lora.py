# SPDX-FileCopyrightText: 2017-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
from functools import reduce
import operator

from httpx import Response
import pytest
import respx
from respx.patterns import M

from mora.lora import Connector

a1_b1 = {"a": 1, "b": 1}
a1_b2 = {"a": 1, "b": 2}
a2_b1 = {"a": 2, "b": 1}
a2_b2 = {"a": 2, "b": 2}


def construct_pattern(args: dict):
    return M(path="/organisation/organisationenhed", **args)


def mock_requests(*args):
    patterns = map(construct_pattern, args)
    pattern = reduce(operator.or_, patterns)

    respx.route(pattern).mock(
        return_value=Response(
            200,
            json={
                "results": [
                    [
                        {"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"},
                    ]
                ],
            },
        )
    )

    respx.get("/organisation/organisationenhed").mock(
        return_value=Response(
            200,
            json={
                "results": [
                    [
                        a1_b1,
                        a1_b2,
                        a2_b1,
                        a2_b2,
                    ]
                ]
            },
        )
    )


# Triggers the startup event `init_clients()` that sets base_url for respx/httpx
@pytest.mark.usefixtures("service_client")
class TestLoraDataLoader:
    @pytest.mark.asyncio
    @respx.mock
    async def test_load_single_param(self):
        mock_requests(dict(json__a=[1, 2]))

        c = Connector()
        load_a1, load_a2, load_a1_again = await asyncio.gather(
            c.organisationenhed.load(a=1),
            c.organisationenhed.load(a=2),
            c.organisationenhed.load(a=1),
        )

        assert load_a1 == load_a1_again == [a1_b1, a1_b2]
        assert load_a2 == [a2_b1, a2_b2]

    @pytest.mark.asyncio
    @respx.mock
    async def test_load_merge_params(self):
        mock_requests(dict(json__a=[1, 2]), dict(json__b=[1, 2]))

        c = Connector()
        load_a1, load_b1, load_a2, load_b2 = await asyncio.gather(
            c.organisationenhed.load(a=1),  # call 0
            c.organisationenhed.load(b=1),  # call 1
            c.organisationenhed.load(a=2),  # call 0
            c.organisationenhed.load(b=2),  # call 1
        )

        assert load_a1 == [a1_b1, a1_b2]
        assert load_a2 == [a2_b1, a2_b2]

        assert load_b1 == [a1_b1, a2_b1]
        assert load_b2 == [a1_b2, a2_b2]

    @pytest.mark.asyncio
    @respx.mock
    async def test_load_multi_params(self):
        mock_requests(dict(json__a=[1]), dict(json__b=[1]))

        c = Connector()
        load_a1, load_a1_b1 = await asyncio.gather(
            c.organisationenhed.load(a=1),  # call 0
            c.organisationenhed.load(a=1, b=1),  # call 1
        )

        assert load_a1 == [a1_b1, a1_b2]
        assert load_a1_b1 == [a1_b1]

    @pytest.mark.asyncio
    @respx.mock
    async def test_load_merge_multi_params(self):
        mock_requests(dict(json__a=[1]), dict(json__a=[1, 2]), dict(json__b=[1]))

        c = Connector()
        load_a1_b1, load_a1_b2, load_b1, load_a1, load_a2_b1 = await asyncio.gather(
            c.organisationenhed.load(a=1, b=1),  # call 0
            c.organisationenhed.load(a=1, b=2),  # call 0
            c.organisationenhed.load(b=1),  # call 1
            c.organisationenhed.load(a=1),  # call 2
            c.organisationenhed.load(a=2, b=1),  # call 0
        )

        assert load_a1_b1 == [a1_b1]
        assert load_a1_b2 == [a1_b2]
        assert load_a2_b1 == [a2_b1]

        assert load_b1 == [a1_b1, a2_b1]
        assert load_a1 == [a1_b1, a1_b2]

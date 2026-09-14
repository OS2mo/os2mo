# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Testing the PBAC extension."""

from asyncio import get_running_loop
from inspect import isawaitable

from mora.graphapi.schema import PBACExtension
from tests.conftest import SetPolicies


async def test_an_answer_already_given_resolves_the_field_where_it_stands(
    set_policies: SetPolicies,
) -> None:
    """A dataloader hitting its cache answers with a future already done."""
    answered = get_running_loop().create_future()
    answered.set_result(True)
    set_policies([lambda root, info, kwargs: answered])

    resolved = PBACExtension().resolve(
        lambda root, info, **kwargs: "the value of the field", None, None
    )

    assert not isawaitable(resolved)
    assert resolved == "the value of the field"


async def test_an_answer_still_pending_is_awaited(set_policies: SetPolicies) -> None:
    """A dataloader with a batch left to run answers with a future still pending."""
    answering = get_running_loop().create_future()
    set_policies([lambda root, info, kwargs: answering])

    resolved = PBACExtension().resolve(
        lambda root, info, **kwargs: "the value of the field", None, None
    )

    assert isawaitable(resolved)
    answering.set_result(True)
    assert await resolved == "the value of the field"

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The rules of the owner policy, translated into CEL."""

from typing import TypeAlias

from mora.graphapi.policy_cel import CEL

MutatorName: TypeAlias = str

OWNER_RULES: list[tuple[MutatorName, CEL]] = []

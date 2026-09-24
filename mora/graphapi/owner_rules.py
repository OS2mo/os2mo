# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The write rules of the owner policy."""

# What each mutator requires owned, read off its arguments, moving here from
# `OWNER_ENTITIES` one mutator at a time
OWNER_RULES: list[tuple[str, str]] = []

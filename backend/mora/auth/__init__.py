# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from strawberry.types import Info


async def is_admin(info: Info) -> bool:
    token = await info.context["get_token"]()
    return "admin" in token.realm_access.roles

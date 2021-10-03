# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry


@strawberry.type
class Organisation:
    uuid: UUID
    name: str
    user_key: str

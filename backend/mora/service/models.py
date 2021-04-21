# SPDX-FileCopyrightText: 2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class MOClass(BaseModel):
    uuid: Optional[UUID]
    name: str
    user_key: str
    scope: Optional[str]
    org_uuid: UUID

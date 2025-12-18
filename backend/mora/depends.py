# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Annotated

from fastapi import Depends
from fastapi import Request
from fastramqpi.ramqp import AMQPSystem as _AMQPSystem

from .db import AsyncSessionWithLock
from .db import get_session

Session = Annotated[AsyncSessionWithLock, Depends(get_session)]


def get_amqp_system(request: Request) -> _AMQPSystem:
    """Extract the AMQPSystem from our app.state.

    Args:
        request: The incoming request.

    Return:
        Extracted AMQPSystem.
    """
    return request.app.state.amqp_system


AMQPSystem = Annotated[_AMQPSystem, Depends(get_amqp_system)]

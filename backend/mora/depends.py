# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Annotated

from fastapi import Depends
from fastapi import Request
from ramqp import AMQPSystem as _AMQPSystem
from sqlalchemy.ext.asyncio import async_sessionmaker as _async_sessionmaker


def get_sessionmaker(request: Request) -> _async_sessionmaker:
    """Extract the sessionmaker from our app.state.

    Args:
        request: The incoming request.

    Return:
        Extracted sessionmaker.
    """
    return request.app.state.sessionmaker


async_sessionmaker = Annotated[_async_sessionmaker, Depends(get_sessionmaker)]


def get_amqp_system(request: Request) -> _AMQPSystem:
    """Extract the AMQPSystem from our app.state.

    Args:
        request: The incoming request.

    Return:
        Extracted AMQPSystem.
    """
    return request.app.state.amqp_system


AMQPSystem = Annotated[_AMQPSystem, Depends(get_amqp_system)]

# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import asyncio
import threading
import typing
from asyncio import set_event_loop
from functools import wraps

from aiohttp import ClientSession

# DROPPED: SAMLAuth() when switching to async (from requests to aiohttp)
# session.auth = flask_saml_sso.SAMLAuth()

# const
headers = {
    'User-Agent': 'MORA/0.1',
}

"""
We use global variables to achieve
    * reuse of async session WHILE running an event loop
"""
_local_cache = threading.local()


def async_session() -> ClientSession:
    """
    lazy (as to wait for someone to set the asyncio event loop), but memoized (global)
    @return:
    """
    global _local_cache
    # Start a session if needed.
    if not hasattr(_local_cache, 'async_session') or _local_cache.async_session is None:
        _local_cache.async_session = ClientSession(headers=headers)
    return _local_cache.async_session


async def __session_context_helper(awaitable) -> typing.Any:
    """
    very defensive function, kills aiohttp sessions before exiting event loop
    technically not needed - an aiohttp.ClientSession CAN survive while its loop is
    restarted, but things can get complicated.

    Also, leaking non-closed sessions is terrible for tests

    :param awaitable: any awaitable
    :return: whatever the awaitable returns
    """
    try:
        ret = await awaitable
    finally:
        # clean-up of global, shared session
        global _local_cache
        # if session was started by the awaitable
        if (
            hasattr(_local_cache,
                    "async_session") and _local_cache.async_session is not None
        ):
            await _local_cache.async_session.close()
            _local_cache.async_session = None
    return ret


def async_to_sync(f):
    """
    Decorator-designed, for 'converting' an async function to a sync function.
    Cannot be used from within an event loop (nested loops are not allowed by asyncio)
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            pass

        if loop is not None:  # debug
            if loop.is_running():  # Explicit error handling to ease debugging
                raise Exception(
                    'asyncio does not allow nested (or reentrant) event loops')

        if loop is None:
            loop = asyncio.new_event_loop()
            set_event_loop(loop)

        return loop.run_until_complete(__session_context_helper(f(*args, **kwargs)))

    return wrapper

# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import threading

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

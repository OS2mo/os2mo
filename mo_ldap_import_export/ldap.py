# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""LDAP Connection handling."""
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from typing import cast
from typing import ContextManager
from typing import Union

import structlog
from fastramqpi.context import Context
from ldap3 import Connection
from ldap3 import NTLM
from ldap3 import RANDOM
from ldap3 import RESTARTABLE
from ldap3 import Server
from ldap3 import ServerPool
from ldap3 import Tls

from .config import ServerConfig
from .config import Settings


def construct_server(server_config: ServerConfig) -> Server:
    """Construct an LDAP3 server from settings.

    Args:
        server_config: The settings to construct the server instance from.

    Returns:
        The constructed server instance used for LDAP connections.
    """
    tls_configuration = Tls(
        validate=CERT_NONE if server_config.insecure else CERT_REQUIRED
    )

    logger = structlog.get_logger()
    logger.info("Setting up server to %s" % server_config.host)
    return Server(
        host=server_config.host,
        port=server_config.port,
        use_ssl=server_config.use_ssl,
        tls=tls_configuration,
        connect_timeout=server_config.timeout,
    )


def get_client_strategy():
    return RESTARTABLE


def configure_ldap_connection(settings: Settings) -> ContextManager:
    """Configure an LDAP connection.

    Args:
        settings: The Settings instance to configure our ad connection with.

    Returns:
        ContextManager that can be opened to establish an LDAP connection.
    """
    servers = list(map(construct_server, settings.ldap_controllers))

    # Pick the next server to use at random, discard non-active servers
    server_pool = ServerPool(servers, RANDOM, active=True, exhaust=True)

    logger = structlog.get_logger()
    logger.info("Connecting to %s" % server_pool)
    logger.info("Client strategy: %s" % get_client_strategy())
    connection = Connection(
        server=server_pool,
        user=settings.ldap_domain + "\\" + settings.ldap_user,
        password=settings.ldap_password.get_secret_value(),
        authentication=NTLM,
        client_strategy=get_client_strategy(),
        auto_bind=True,
    )

    return cast(ContextManager, connection)


async def ldap_healthcheck(context: Union[dict, Context]) -> bool:
    """LDAP connection Healthcheck.

    Args:
        context: To lookup ldap_connection in.

    Returns:
        Whether the AMQPSystem is OK.
    """
    ldap_connection = context["user_context"]["ldap_connection"]
    return cast(bool, ldap_connection.bound)

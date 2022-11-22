# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""LDAP Connection handling."""
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from typing import Any
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
from more_itertools import always_iterable
from more_itertools import only

from .config import ServerConfig
from .config import Settings
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .ldap_classes import LdapObject


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
    host = server_config.host
    logger.info(f"Setting up server to {host}")
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
    client_strategy = get_client_strategy()

    logger = structlog.get_logger()
    logger.info(f"Connecting to {server_pool}")
    logger.info(f"Client strategy: {client_strategy}")
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


def get_ldap_schema(ldap_connection: Connection):
    return ldap_connection.server.schema


def get_ldap_object_schema(ldap_connection: Connection, ldap_object: str):
    schema = get_ldap_schema(ldap_connection)
    return schema.object_classes[ldap_object]


def get_ldap_superiors(ldap_connection: Connection, root_ldap_object: str):

    superiors = []
    ldap_object: Union[str, None] = root_ldap_object
    while ldap_object is not None:
        object_schema = get_ldap_object_schema(ldap_connection, ldap_object)
        ldap_object = only(always_iterable(object_schema.superior))
        if ldap_object is not None:
            superiors.append(ldap_object)

    return superiors


def get_ldap_attributes(ldap_connection: Connection, root_ldap_object: str):
    """
    ldap_connection : ldap connection object
    ldap_object : ldap class to fetch attributes for. for example "organizationalPerson"
    """

    logger = structlog.get_logger()
    all_attributes = []
    superiors = get_ldap_superiors(ldap_connection, root_ldap_object)

    for ldap_object in [root_ldap_object] + superiors:
        object_schema = get_ldap_object_schema(ldap_connection, ldap_object)
        if ldap_object != "top":
            logger.info(f"Fetching allowed objects for {ldap_object}")
            all_attributes += object_schema.may_contain
    return all_attributes


def paged_search(context: Context, searchParameters: dict) -> list:
    """
    searchParameters : dict
        Dict with the following keys:
            * search_filter
            * attributes
    """
    responses = []
    logger = structlog.get_logger()

    user_context = context["user_context"]
    search_base = user_context["settings"].ldap_search_base
    ldap_connection = user_context["ldap_connection"]

    # TODO: Find max. paged_size number from LDAP rather than hard-code it?
    searchParameters["paged_size"] = 500
    searchParameters["search_base"] = search_base

    search_filter = searchParameters["search_filter"]
    search_base = searchParameters["search_base"]

    logger.info(f"searching for {search_filter} on {search_base}")

    # Max 10_000 pages to avoid eternal loops
    for page in range(0, 10_000):
        logger.info(f"searching page {page}")
        ldap_connection.search(**searchParameters)

        if ldap_connection.result["description"] == "operationsError":
            logger.warn(f"{search_filter} Search failed")
            break

        entries = [r for r in ldap_connection.response if r["type"] == "searchResEntry"]
        responses.extend(entries)

        # TODO: Skal "1.2.840.113556.1.4.319" være Configurerbar?
        cookie = ldap_connection.result["controls"]["1.2.840.113556.1.4.319"]["value"][
            "cookie"
        ]

        if cookie and type(cookie) is bytes:
            searchParameters["paged_cookie"] = cookie
        else:
            break

    return responses


def single_object_search(searchParameters, ldap_connection):
    """
    Performs an LDAP search and throws an exception if there are multiple or no search
    results.

    Parameters
    -------------
    searchParameters : dict
        Dict with the following keys:
            * search_base
            * search_filter
            * attributes
            * see https://ldap3.readthedocs.io/en/latest/searches.html for more keys

    Notes
    ------
    If you want to be 100% sure that the search only returns one result; Supply an
    object's dn (distinguished name) as the search base.
    """
    ldap_connection.search(**searchParameters)
    response = ldap_connection.response
    logger = structlog.get_logger()

    search_entries = [r for r in response if r["type"] == "searchResEntry"]

    if len(search_entries) > 1:
        logger.info(response)
        raise MultipleObjectsReturnedException(
            f"Found multiple entries for {searchParameters}"
        )
    elif len(search_entries) == 0:
        logger.info(response)
        raise NoObjectsReturnedException(f"Found no entries for {searchParameters}")
    else:
        return search_entries[0]


def is_dn(value):
    """
    Determine if a value is a dn (distinguished name) string
    """
    if type(value) is not str:
        return False

    parts = value.split(",")
    for required in ("CN=", "OU=", "DC="):
        found = False
        for part in parts:
            if part.strip().startswith(required):
                found = True
                break
        if not found:
            return False
    return True


def get_ldap_object(dn, context, nest=True):
    """
    Gets a ldap object based on its DN

    if nest is True, also gets ldap objects of related objects.
    """
    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]
    logger = structlog.get_logger()

    searchParameters = {
        "search_base": dn,
        "search_filter": "(objectclass=*)",
        "attributes": ["*"],
    }
    search_result = single_object_search(searchParameters, ldap_connection)
    dn = search_result["dn"]
    logger.info(f"[get_ldap_object] Found {dn}")
    return make_ldap_object(search_result, context, nest=nest)


def make_ldap_object(response: dict, context: Context, nest=True) -> Any:
    """
    Takes an ldap response and formats it as a class

    if nest is True, also makes ldap objects of related objects.
    """
    attributes = list(response["attributes"].keys())
    ldap_dict = {"dn": response["dn"]}

    def get_nested_ldap_object(dn):
        """
        Gets a ldap object based on its DN - unless we are in a nested loop
        """

        if nest:
            return get_ldap_object(dn, context, nest=False)
        else:  # pragma: no cover
            raise Exception("Already running in nested loop")

    def is_other_dn(value):
        """
        Determine if the value is a dn (distinguished name)
        But not the dn of the main object itself

        This is to avoid that the code requests information about itself
        """
        return is_dn(value) and value != response["dn"]

    for attribute in attributes:
        value = response["attributes"][attribute]
        if is_other_dn(value) and nest:
            ldap_dict[attribute] = get_nested_ldap_object(value)
        elif type(value) is list:
            ldap_dict[attribute] = [
                get_nested_ldap_object(v) if is_other_dn(v) and nest else v
                for v in value
            ]
        else:
            ldap_dict[attribute] = value

    return LdapObject(**ldap_dict)

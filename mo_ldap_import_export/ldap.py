# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""LDAP Connection handling."""
import asyncio
import signal
from collections import ChainMap
from contextlib import suppress
from datetime import datetime
from functools import partial
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from threading import Thread
from typing import Any
from typing import cast
from uuid import UUID

import ldap3.core.exceptions
import structlog
from fastramqpi.context import Context
from fastramqpi.depends import UserContext
from fastramqpi.ramqp import AMQPSystem
from ldap3 import BASE
from ldap3 import Connection
from ldap3 import NTLM
from ldap3 import RANDOM
from ldap3 import RESTARTABLE
from ldap3 import Server
from ldap3 import ServerPool
from ldap3 import SIMPLE
from ldap3 import Tls
from ldap3.core.exceptions import LDAPInvalidDnError
from ldap3.utils.dn import parse_dn
from ldap3.utils.dn import safe_dn
from more_itertools import always_iterable
from more_itertools import one
from ramodels.mo.employee import Employee

from .config import AuthBackendEnum
from .config import ServerConfig
from .config import Settings
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .exceptions import TimeOutException
from .ldap_classes import LdapObject
from .processors import _hide_cpr as hide_cpr
from .utils import combine_dn_strings
from .utils import datetime_to_ldap_timestamp
from .utils import ensure_list
from .utils import is_list
from .utils import mo_object_is_valid

logger = structlog.stdlib.get_logger()


def construct_server(server_config: ServerConfig) -> Server:
    """Construct an LDAP3 server from settings.

    Args:
        server_config: The settings to construct the server instance from.

    Returns:
        The constructed server instance used for LDAP connections.
    """
    tls_configuration = Tls(
        validate=CERT_NONE if server_config.insecure else CERT_REQUIRED,
        ca_certs_data=server_config.ca_certs_data,
    )

    host = server_config.host
    logger.info("Setting up server", host=host)
    return Server(
        host=server_config.host,
        port=server_config.port,
        use_ssl=server_config.use_ssl,
        tls=tls_configuration,
        connect_timeout=server_config.timeout,
    )


def get_client_strategy():
    return RESTARTABLE


def construct_server_pool(settings: Settings) -> ServerPool:
    servers = list(map(construct_server, settings.ldap_controllers))
    # Pick the next server to use at random, retry connections 10 times,
    # discard non-active servers.
    server_pool = ServerPool(
        servers,
        RANDOM,
        active=10,  # type: ignore[arg-type]
        exhaust=True,
    )
    return server_pool


def configure_ldap_connection(settings: Settings) -> Connection:
    """Configure an LDAP connection.

    Args:
        settings: The Settings instance to configure our ad connection with.

    Returns:
        ContextManager that can be opened to establish an LDAP connection.
    """

    def alarm_handler(signum, frame):
        raise TimeOutException(
            "Timeout while configuring LDAP connection. Try 'sudo tailscale up'?"
        )

    # Set a timeout alarm
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(max([c.timeout for c in settings.ldap_controllers]))

    server_pool = construct_server_pool(settings)
    client_strategy = get_client_strategy()

    logger.info(
        "Connecting to server",
        server_pool=server_pool,
        client_strategy=client_strategy,
        auth_strategy=settings.ldap_auth_method.value,
    )

    connection_kwargs = {
        "server": server_pool,
        "client_strategy": get_client_strategy(),
        "password": settings.ldap_password.get_secret_value(),
        "auto_bind": True,
        # NOTE: It appears that this flag does not in fact work
        # See: https://github.com/cannatag/ldap3/issues/1008
        "read_only": settings.ldap_read_only,
    }
    match settings.ldap_auth_method:
        case AuthBackendEnum.NTLM:
            connection_kwargs.update(
                {
                    "user": settings.ldap_domain + "\\" + settings.ldap_user,
                    "authentication": NTLM,
                }
            )
        case AuthBackendEnum.SIMPLE:
            connection_kwargs.update(
                {
                    "user": settings.ldap_user,
                    "authentication": SIMPLE,
                }
            )
        case _:
            # Turn off the alarm
            signal.alarm(0)
            raise ValueError("Unknown authentication backend")

    try:
        connection = Connection(**connection_kwargs)
    except ldap3.core.exceptions.LDAPBindError as exc:
        logger.exception("Exception during LDAP auth")
        raise exc
    finally:
        # Turn off the alarm
        signal.alarm(0)

    return connection


async def ldap_healthcheck(context: dict | Context) -> bool:
    """LDAP connection Healthcheck.

    Args:
        context: To lookup ldap_connection in.

    Returns:
        Whether the LDAP connection is OK.
    """
    ldap_connection = context["user_context"]["ldap_connection"]
    return cast(bool, ldap_connection.bound)


async def poller_healthcheck(context: dict | Context) -> bool:
    pollers = context["user_context"]["pollers"]
    return all(not poller.done() for poller in pollers)


def get_ldap_schema(ldap_connection: Connection):
    return ldap_connection.server.schema


def get_ldap_object_schema(ldap_connection: Connection, ldap_object: str):
    schema = get_ldap_schema(ldap_connection)
    return schema.object_classes[ldap_object]


def get_ldap_superiors(ldap_connection: Connection, root_ldap_object: str) -> list:
    object_schema = get_ldap_object_schema(ldap_connection, root_ldap_object)
    ldap_objects = list(always_iterable(object_schema.superior))
    superiors = []
    for ldap_object in ldap_objects:
        superiors.append(ldap_object)
        superiors.extend(get_ldap_superiors(ldap_connection, ldap_object))
    return superiors


def get_ldap_attributes(ldap_connection: Connection, root_ldap_object: str):
    """
    ldap_connection : ldap connection object
    ldap_object : ldap class to fetch attributes for. for example "organizationalPerson"
    """

    all_attributes = []
    superiors = get_ldap_superiors(ldap_connection, root_ldap_object)

    for ldap_object in [root_ldap_object] + superiors:
        object_schema = get_ldap_object_schema(ldap_connection, ldap_object)
        all_attributes += object_schema.may_contain
    return all_attributes


def apply_discriminator(
    search_result: list[dict[str, Any]], settings: Settings
) -> list[dict[str, Any]]:
    """Apply our discriminator to remove unwanted search result.

    Args:
        search_result: A list of LDAP search results.
        settings: The application settings.

    Returns:
        A filtered list of LDAP search results.
    """
    discriminator_field = settings.discriminator_field
    discriminator_values = settings.discriminator_values
    match settings.discriminator_function:
        case None:
            return search_result

        case "include":

            def discriminator(res: Any) -> bool:
                attributes = res["attributes"]
                return (
                    discriminator_field in attributes
                    and str(attributes[discriminator_field]) in discriminator_values
                )

        case "exclude":

            def discriminator(res: Any) -> bool:
                attributes = res["attributes"]
                return (
                    discriminator_field not in attributes
                    or str(attributes[discriminator_field]) not in discriminator_values
                )

        case _:  # pragma: no cover
            assert False

    return list(filter(discriminator, search_result))


def ldapresponse2entries(ldap_response: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # TODO: Handle other response types
    # See: https://ldap3.readthedocs.io/en/latest/searches.html#response
    return [entry for entry in ldap_response if entry["type"] == "searchResEntry"]


def _paged_search(
    settings: Settings,
    ldap_connection: Connection,
    searchParameters: dict,
    search_base: str,
    mute: bool,
) -> list:
    # TODO: Eliminate mute argument? - Should be logger configuration?
    # TODO: Find max. paged_size number from LDAP rather than hard-code it?
    searchParameters["paged_size"] = 500
    searchParameters["search_base"] = search_base

    search_filter = searchParameters["search_filter"]

    if not mute:
        logger.info(
            "Executing paged_search",
            search_filter=search_filter,
            search_base=search_base,
        )

    # Max 10_000 pages to avoid eternal loops
    # TODO: Why would we get eternal loops?
    responses = []
    for page in range(0, 10_000):
        if not mute:
            logger.info("Searching page", page=page)
        ldap_connection.search(**searchParameters)

        if ldap_connection.result["description"] == "operationsError":
            # TODO: Should this be an exception?
            #       Currently we just return half the result?
            logger.warn(
                "Search failed",
                search_filter=search_filter,
                result=ldap_connection.result,
            )
            break

        # TODO: Handle this error more gracefully
        assert ldap_connection.response is not None
        entries = ldapresponse2entries(ldap_connection.response)
        entries = apply_discriminator(entries, settings)
        responses.extend(entries)

        try:
            # TODO: Skal "1.2.840.113556.1.4.319" være Configurerbar?
            extension = "1.2.840.113556.1.4.319"
            cookie = ldap_connection.result["controls"][extension]["value"]["cookie"]
        except KeyError:
            break

        if cookie and isinstance(cookie, bytes):
            searchParameters["paged_cookie"] = cookie
        else:
            break

    return responses


def paged_search(
    context: Context,
    searchParameters: dict,
    search_base: str | None = None,
    mute: bool = False,
) -> list:
    """
    Execute a search on the LDAP server.

    Args:
        context: The FastRAMQPI context.
        searchParameters:
            Dict with the following keys:
                * search_filter
                * attributes
        search_base:
            Search base to search in.
            If empty, uses settings.search_base combined with settings.ous_to_search_in.
        mute: Whether to log process information

    Returns:
        A list of search results.
    """
    # NOTE: It seems like this function is purely used for manual endpoints
    #       Except from a single call from usernames.py
    # TODO: Consider moving this to its own module separate from business logic
    # TODO: Make a class for the searchParameters if it has a fixed format?

    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]
    settings = user_context["settings"]

    if search_base:
        # If the search base is explicitly defined: Don't try anything fancy.
        results = _paged_search(
            settings, ldap_connection, searchParameters, search_base, mute
        )
        return results

    # Otherwise, loop over all OUs to search in
    search_bases = [
        combine_dn_strings([ou, settings.ldap_search_base])
        for ou in settings.ldap_ous_to_search_in
    ]
    results = []
    for search_base in search_bases:
        results.extend(
            _paged_search(
                settings, ldap_connection, searchParameters.copy(), search_base, mute
            )
        )

    return results


def object_search(
    searchParameters: dict[str, Any], ldap_connection: Connection
) -> list[dict[str, Any]]:
    """Performs an LDAP search and return the result.

    Notes:
        If you want to be 100% sure that the search only returns one result;
        Supply an object's dn (distinguished name) as the search base and set
        searchFilter = "(objectclass=*)" and search_scope = BASE

    Args:
        searchParameters:
            Dictionary with the following keys:
                * search_base
                * search_filter
                * attributes
                * see https://ldap3.readthedocs.io/en/latest/searches.html for more keys
        ldap_connection: The LDAP Connection to run our search on.

    Returns:
        A list of found objects.
    """
    search_bases = ensure_list(searchParameters["search_base"])

    responses = []
    for search_base in search_bases:
        ldap_connection.search(
            **ChainMap(searchParameters, {"search_base": search_base})
        )
        response = ldap_connection.response
        if response:
            responses.extend(response)
    search_entries = ldapresponse2entries(responses)
    return search_entries


def single_object_search(
    searchParameters: dict[str, Any], context: Context
) -> dict[str, Any]:
    """Performs an LDAP search and ensure that it returns one result.

    Notes:
        If you want to be 100% sure that the search only returns one result;
        Supply an object's dn (distinguished name) as the search base and set
        searchFilter = "(objectclass=*)" and search_scope = BASE

    Args:
        searchParameters:
            Dictionary with the following keys:
                * search_base
                * search_filter
                * attributes
                * see https://ldap3.readthedocs.io/en/latest/searches.html for more keys
        context: The FastRAMQPI context.

    Raises:
        MultipleObjectsReturnedException: If multiple objects were found.
        NoObjectsReturnedException: If no objects were found.

    Returns:
        The found object.
    """
    ldap_connection = context["user_context"]["ldap_connection"]
    search_entries = object_search(searchParameters, ldap_connection)

    settings = context["user_context"]["settings"]
    # TODO: Do we actually wanna apply discriminator here?
    search_entries = apply_discriminator(search_entries, settings)

    too_long_exception = MultipleObjectsReturnedException(
        hide_cpr(f"Found multiple entries for {searchParameters}: {search_entries}")
    )
    too_short_exception = NoObjectsReturnedException(
        hide_cpr(f"Found no entries for {searchParameters}")
    )
    return one(
        search_entries, too_short=too_short_exception, too_long=too_long_exception
    )


def is_dn(value):
    """
    Determine if a value is a dn (distinguished name) string
    """
    if not isinstance(value, str):
        return False

    try:
        safe_dn(value)
        parse_dn(value)
    except LDAPInvalidDnError:
        return False
    return True


def get_ldap_object(dn: str, context: Context, nest: bool = True) -> Any:
    """
    Gets a ldap object based on its DN

    if nest is True, also gets ldap objects of related objects.
    """
    searchParameters = {
        "search_base": dn,
        "search_filter": "(objectclass=*)",
        "attributes": ["*"],
        "search_scope": BASE,
    }
    search_result = single_object_search(searchParameters, context)
    dn = search_result["dn"]
    logger.info("Found DN", dn=dn)
    return make_ldap_object(search_result, context, nest=nest)


def make_ldap_object(response: dict, context: Context, nest: bool = True) -> Any:
    """
    Takes an ldap response and formats it as a class

    if nest is True, also makes ldap objects of related objects.
    """
    attributes = sorted(list(response["attributes"].keys()))
    ldap_dict = {"dn": response["dn"]}

    def get_nested_ldap_object(dn):
        """
        Gets a ldap object based on its DN - unless we are in a nested loop
        """

        if nest:
            logger.info("Loading nested ldap object", dn=dn)
            return get_ldap_object(dn, context, nest=False)
        raise Exception("Already running in nested loop")  # pragma: no cover

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
        elif is_list(value):
            ldap_dict[attribute] = [
                get_nested_ldap_object(v) if is_other_dn(v) and nest else v
                for v in value
            ]
        else:
            ldap_dict[attribute] = value

    return LdapObject(**ldap_dict)


def get_attribute_types(ldap_connection):
    """
    Returns a dictionary with attribute type information for all attributes in LDAP
    """
    return ldap_connection.server.schema.attribute_types


async def cleanup(
    json_key: str,
    mo_dict_key: str,
    mo_objects: list[Any],
    user_context: dict,
    employee: Employee,
    object_type: str,
    dn: str,
):
    """
    Cleans entries from LDAP

    json_key : str
        json key to clean for
    value_key : str
        name of the MO attribute that contains the value to be cleaned
    mo_dict_key : str
        name of the key in the conversion dict. i.e. 'mo_employee'
        or 'mo_employee_address'
    mo_objects: list
        List of objects already in MO
    user_context : dict
        user context dictionary with the configured dataloader and converter
    """
    from .dataloaders import DataLoader

    dataloader: DataLoader = user_context["dataloader"]
    converter = user_context["converter"]
    sync_tool = user_context["sync_tool"]

    if not converter._export_to_ldap_(json_key):
        logger.info("_export_to_ldap_ == False", json_key=json_key)
        return

    # Get matching LDAP object for this user (note that LDAP can contain
    # multiple entries in one object)
    attributes = converter.get_ldap_attributes(json_key)
    ldap_object = dataloader.load_ldap_object(dn, attributes)

    logger.info("Found data in LDAP", ldap_object=ldap_object)

    mo_objects = list(filter(mo_object_is_valid, mo_objects))

    # Convert to LDAP-style to make mo-data comparable to LDAP data.
    converted_mo_objects = [
        await converter.to_ldap(
            {
                "mo_employee": employee,
                mo_dict_key: mo_object,
            },
            json_key,
            dn,
        )
        for mo_object in mo_objects
    ]
    logger.info("Found data in MO", mo_object=converted_mo_objects)

    # Loop over each attribute and determine if it needs to be cleaned
    uuids_to_publish: set[UUID] = set()
    ldap_objects_to_clean = []
    for attribute in attributes:
        values_in_ldap = getattr(ldap_object, attribute)
        values_in_mo: list[Any] = list(
            filter(None, [getattr(o, attribute, None) for o in converted_mo_objects])
        )

        if not is_list(values_in_ldap):
            values_in_ldap = [values_in_ldap] if values_in_ldap else []

        # If a value is in LDAP but NOT in MO, it needs to be cleaned
        for value_in_ldap in values_in_ldap:
            if (
                value_in_ldap not in values_in_mo
                and str(value_in_ldap) not in values_in_mo
            ):
                logger.info(
                    "Attribute value needs cleaning",
                    attribute=attribute,
                    value=value_in_ldap,
                )
                ldap_objects_to_clean.append(
                    LdapObject(**{"dn": dn, attribute: value_in_ldap})
                )

        # If MO contains values and LDAP doesn't, send AMQP messages to export to LDAP
        # This can happen, if we delete an address in MO, and another address already
        # exists in MO. In that case the other address should be written to LDAP,
        # after the first one is deleted from LDAP
        if not values_in_ldap and values_in_mo:
            logger.info("Attribute needs to be written to LDAP", attribute=attribute)
            uuids_to_publish.update(o.uuid for o in mo_objects)

    # Clean from LDAP
    if len(ldap_objects_to_clean) == 0:
        logger.info("No cleanup required")
    else:
        dataloader.cleanup_attributes_in_ldap(ldap_objects_to_clean)

    # Publish to internal AMQP system
    for uuid in uuids_to_publish:
        await sync_tool.refresh_object(uuid, object_type)


def setup_listener(context: Context) -> list[Thread]:
    user_context = context["user_context"]

    # Note:
    # We need the dn attribute to trigger sync_tool.import_single_user()
    # We need the modifyTimeStamp attribute to check for duplicate events in _poller()
    settings = user_context["settings"]
    pollers = []
    for ldap_ou_to_scan_for_changes in settings.ldap_ous_to_search_in:
        search_base = combine_dn_strings(
            [ldap_ou_to_scan_for_changes, settings.ldap_search_base]
        )

        search_parameters = {
            "search_base": search_base,
            "search_filter": "(cn=*)",
            "attributes": ["distinguishedName"],
        }

        # Polling search
        pollers.append(
            setup_poller(
                user_context,
                search_parameters,
                datetime.utcnow(),
                settings.poll_time,
            )
        )
    return pollers


def setup_poller(
    user_context: UserContext,
    search_parameters: dict,
    init_search_time: datetime,
    poll_time: float,
) -> Any:
    def done_callback(future):
        # This ensures exceptions go to the terminal
        future.result()

    handle = asyncio.create_task(
        _poller(user_context, search_parameters, init_search_time, poll_time)
    )
    handle.add_done_callback(done_callback)
    return handle


async def _poll(
    user_context: UserContext,
    search_parameters: dict,
    last_search_time: datetime,
) -> datetime:
    """Pool the LDAP server for changes once.

    Args:
        context:
            The entire settings context.
        search_params:
            LDAP search parameters.
        callback:
            Function to call with all changes since `last_search_time`.
        last_search_time:
            Find events that occured since this time.

    Returns:
        A two-tuple containing a list of events to ignore and the time at
        which the last search was done.

        Should be provided as `last_search_time` in the next iteration.
    """
    ldap_amqpsystem: AMQPSystem = user_context["ldap_amqpsystem"]
    ldap_connection = user_context["ldap_connection"]

    logger.debug(
        "Searching for changes since last search", last_search_time=last_search_time
    )
    timed_search_parameters = set_search_params_modify_timestamp(
        search_parameters, last_search_time
    )
    last_search_time = datetime.utcnow()

    # TODO: Eliminate this thread and use asyncio code instead
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None, partial(ldap_connection.search, **timed_search_parameters)
    )

    # Filter to only keep search results
    responses = ldapresponse2entries(ldap_connection.response)

    # NOTE: We can add message deduplication here if needed for performance later
    #       For now we do not care about duplicates, we prefer simplicity
    #       See: !499 for details

    def event2dn(event: dict[str, Any]) -> str | None:
        dn = event.get("attributes", {}).get("distinguishedName", None)
        dn = dn or event.get("dn", None)
        if dn is None:
            logger.warning("Got event without dn")
        return cast(str | None, dn)

    dns = [event2dn(event) for event in responses]
    dns = [dn for dn in dns if dn is not None]
    if dns:
        logger.info("Registered change for LDAP object(s)", dns=dns)
        await asyncio.gather(*[ldap_amqpsystem.publish_message("dn", dn) for dn in dns])

    return last_search_time


async def _poller(
    user_context: UserContext,
    search_parameters: dict,
    init_search_time: datetime,
    poll_time: float,
) -> None:
    """Poll the LDAP server continuously every `poll_time` seconds.

    Args:
        context:
            The entire settings context.
        search_params:
            LDAP search parameters.
        callback:
            Function to call with all changes since `last_search_time`.
        init_search_time:
            Find events that occured since this time.
        pool_time:
            The interval with which to poll.
    """
    logger.info("Poller started", search_base=search_parameters["search_base"])

    seeded_poller = partial(
        _poll,
        user_context=user_context,
        search_parameters=search_parameters,
    )

    last_search_time = init_search_time
    while True:
        last_search_time = await seeded_poller(last_search_time=last_search_time)
        await asyncio.sleep(poll_time)


def set_search_params_modify_timestamp(
    search_parameters: dict[str, str], timestamp: datetime
) -> dict[str, str]:
    changed_str = f"(modifyTimestamp>={datetime_to_ldap_timestamp(timestamp)})"
    search_filter = search_parameters["search_filter"]
    if not search_filter.startswith("(") or not search_filter.endswith(")"):
        search_filter = f"({search_filter})"
    return {
        **search_parameters,
        "search_filter": "(&" + changed_str + search_filter + ")",
    }


def is_uuid(entity: Any) -> bool:
    """
    Check if a entity is a valid UUID
    """
    with suppress(ValueError):
        UUID(str(entity))
        return True
    return False


def check_ou_in_list_of_ous(ou_to_check, list_of_ous):
    """
    Checks if a specific OU exists in a list of OUs. Raises ValueError if it does not
    """
    any_ok = any(ou_to_check.endswith(ou) for ou in list_of_ous)
    if not any_ok:
        raise ValueError(f"{ou_to_check} is not in {list_of_ous}")

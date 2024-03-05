# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
"""LDAP Connection handling."""
import signal
import time
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime
from functools import partial
from ssl import CERT_NONE
from ssl import CERT_REQUIRED
from threading import Thread
from typing import Any
from typing import cast
from typing import ContextManager
from uuid import UUID

import ldap3.core.exceptions
from fastramqpi.context import Context
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
from ramodels.mo.employee import Employee

from .config import AuthBackendEnum
from .config import ServerConfig
from .config import Settings
from .exceptions import MultipleObjectsReturnedException
from .exceptions import NoObjectsReturnedException
from .exceptions import TimeOutException
from .ldap_classes import LdapObject
from .logging import logger
from .processors import _hide_cpr as hide_cpr
from .utils import combine_dn_strings
from .utils import datetime_to_ldap_timestamp
from .utils import mo_object_is_valid


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

    def alarm_handler(signum, frame):
        raise TimeOutException(
            "Timeout while configuring LDAP connection. Try 'sudo tailscale up'?"
        )

    # Set a timeout alarm
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(max([c.timeout for c in settings.ldap_controllers]))

    servers = list(map(construct_server, settings.ldap_controllers))

    # Pick the next server to use at random, discard non-active servers
    server_pool = ServerPool(servers, RANDOM, active=True, exhaust=True)
    client_strategy = get_client_strategy()

    logger.info(f"Connecting to {server_pool}")
    logger.info(f"Client strategy: {client_strategy}")
    logger.info(f"Auth strategy: {settings.ldap_auth_method.value}")

    connection_kwargs = {
        "server": server_pool,
        "client_strategy": get_client_strategy(),
        "password": settings.ldap_password.get_secret_value(),
        "auto_bind": True,
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
        logger.error("Exception during LDAP auth", exc_info=exc)
        raise exc
    finally:
        # Turn off the alarm
        signal.alarm(0)

    return cast(ContextManager, connection)


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
    return all(poller.is_alive() for poller in pollers)


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


def apply_discriminator(search_result: list, context: Context) -> list:
    settings = context["user_context"]["settings"]

    discriminator_field = settings.discriminator_field
    discriminator_values = settings.discriminator_values
    match settings.discriminator_function:
        case None:
            return search_result
        case "include":

            def discriminator(res: Any) -> bool:
                return (
                    discriminator_field in res
                    and str(res[discriminator_field]) in discriminator_values
                )

        case "exclude":

            def discriminator(res: Any) -> bool:
                return (
                    discriminator_field not in res
                    or str(res[discriminator_field]) not in discriminator_values
                )

        case _:  # pragma: no cover
            assert False

    return list(filter(discriminator, search_result))


def _paged_search(
    context: Context,
    searchParameters: dict,
    search_base: str,
    mute: bool = False,
) -> list:
    responses = []
    user_context = context["user_context"]
    ldap_connection = user_context["ldap_connection"]

    # TODO: Find max. paged_size number from LDAP rather than hard-code it?
    searchParameters["paged_size"] = 500
    searchParameters["search_base"] = search_base

    search_filter = searchParameters["search_filter"]

    if not mute:
        logger.info(f"searching for {search_filter} on {search_base}")

    # Max 10_000 pages to avoid eternal loops
    for page in range(0, 10_000):
        if not mute:
            logger.info(f"searching page {page}")
        ldap_connection.search(**searchParameters)

        if ldap_connection.result["description"] == "operationsError":
            logger.warn(f"{search_filter} Search failed")
            logger.warn(ldap_connection.result)
            break

        entries = [r for r in ldap_connection.response if r["type"] == "searchResEntry"]
        entries = apply_discriminator(entries, context)
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
    **kwargs,
) -> list:
    """
    Parameters
    -----------------
    searchParameters : dict
        Dict with the following keys:
            * search_filter
            * attributes
    search_base : str
        Search base to search in. If empty, uses settings.search_base combined with
        settings.ous_to_search_in
    """

    if search_base:
        # If the search base is explicitly defined: Don't try anything fancy.
        results = _paged_search(context, searchParameters, search_base, **kwargs)
    else:
        # Otherwise, loop over all OUs to search in
        settings = context["user_context"]["settings"]

        results = []
        for ou in settings.ldap_ous_to_search_in:
            search_base = combine_dn_strings([ou, settings.ldap_search_base])
            results.extend(
                _paged_search(context, searchParameters.copy(), search_base, **kwargs)
            )

    return results


def single_object_search(searchParameters, context: Context):
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
    object's dn (distinguished name) as the search base and set
    searchFilter = "(objectclass=*)" and search_scope = BASE
    """
    ldap_connection = context["user_context"]["ldap_connection"]
    if isinstance(searchParameters["search_base"], list):
        search_bases = searchParameters["search_base"].copy()
        modified_searchParameters = searchParameters.copy()
        response = []
        for search_base in search_bases:
            modified_searchParameters["search_base"] = search_base
            ldap_connection.search(**modified_searchParameters)
            response.extend(ldap_connection.response)
    else:
        ldap_connection.search(**searchParameters)
        response = ldap_connection.response

    search_entries = [r for r in response if r["type"] == "searchResEntry"]

    search_entries = apply_discriminator(search_entries, context)

    if len(search_entries) > 1:
        logger.info(response)
        raise MultipleObjectsReturnedException(
            hide_cpr(f"Found multiple entries for {searchParameters}: {search_entries}")
        )
    elif len(search_entries) == 0:
        logger.info(response)
        raise NoObjectsReturnedException(
            hide_cpr(f"Found no entries for {searchParameters}")
        )
    else:
        return search_entries[0]


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
    else:
        return True


def get_ldap_object(dn, context, nest=True):
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
    logger.info(f"[get_ldap_object] Found {dn}")
    return make_ldap_object(search_result, context, nest=nest)


def make_ldap_object(response: dict, context: Context, nest=True) -> Any:
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
            logger.info(f"[make_ldap_object] Loading nested ldap object with dn={dn}")
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
        elif isinstance(value, list):
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
    dataloader = user_context["dataloader"]
    converter = user_context["converter"]
    sync_tool = user_context["sync_tool"]
    uuids_to_publish = []

    if not converter._export_to_ldap_(json_key):
        logger.info(f"_export_to_ldap_ == False for json_key = '{json_key}'")
        return

    # Get matching LDAP object for this user (note that LDAP can contain
    # multiple entries in one object)
    attributes = converter.get_ldap_attributes(json_key)
    ldap_object = dataloader.load_ldap_object(dn, attributes)

    logger.info(f"Found the following data in LDAP: {ldap_object}")

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
    logger.info(f"Found the following data in MO: {converted_mo_objects}")

    # Loop over each attribute and determine if it needs to be cleaned
    ldap_objects_to_clean = []
    for attribute in attributes:
        values_in_ldap = getattr(ldap_object, attribute)
        values_in_mo: list[Any] = list(
            filter(None, [getattr(o, attribute, None) for o in converted_mo_objects])
        )

        if not isinstance(values_in_ldap, list):
            values_in_ldap = [values_in_ldap] if values_in_ldap else []

        # If a value is in LDAP but NOT in MO, it needs to be cleaned
        for value_in_ldap in values_in_ldap:
            if (
                value_in_ldap not in values_in_mo
                and str(value_in_ldap) not in values_in_mo
            ):
                logger.info(f"{attribute} = '{value_in_ldap}' needs cleaning")
                ldap_objects_to_clean.append(
                    LdapObject(**{"dn": dn, attribute: value_in_ldap})
                )

        # If MO contains values and LDAP doesn't, send AMQP messages to export to LDAP
        # This can happen, if we delete an address in MO, and another address already
        # exists in MO. In that case the other address should be written to LDAP,
        # after the first one is deleted from LDAP
        if not values_in_ldap and values_in_mo:
            logger.info(f"attribute = '{attribute}' needs to be written to LDAP")
            uuids_to_publish = [o.uuid for o in mo_objects]

    # Clean from LDAP
    if len(ldap_objects_to_clean) == 0:
        logger.info("No cleanup required")
    else:
        dataloader.cleanup_attributes_in_ldap(ldap_objects_to_clean)

    # Publish to internal AMQP system
    for uuid in uuids_to_publish:
        await sync_tool.refresh_object(uuid, object_type)


def setup_listener(context: Context, callback: Callable) -> list[Thread]:
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
            "attributes": ["distinguishedName", "modifyTimestamp"],
        }

        # Polling search
        pollers.append(
            setup_poller(
                context,
                callback,
                search_parameters,
                datetime.utcnow(),
                user_context["poll_time"],
            )
        )
    return pollers


def setup_poller(
    context: Context,
    callback: Callable,
    search_parameters: dict,
    init_search_time: datetime,
    poll_time: float,
) -> Thread:
    # TODO: Eliminate this thread and use asyncio code instead
    poll = Thread(
        target=_poller,
        args=(
            context,
            search_parameters,
            callback,
            init_search_time,
            poll_time,
        ),
        daemon=True,
    )
    poll.start()
    return poll


def _poll(
    context: Context,
    search_parameters: dict,
    callback: Callable,
    last_search_time: datetime,
    events_to_ignore: list[Any],
) -> tuple[list[Any], datetime]:
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
        events_to_ignore:
            Ignore events in this list. Used to remove duplicate events.

    Returns:
        A two-tuple containing a list of events to ignore and the time at
        which the last search was done.

        Should be provided as `last_search_time` and `events_to_ignore` in the
        next iteration.
    """
    ldap_connection = context["user_context"]["ldap_connection"]

    logger.debug(f"Searching for changes since {last_search_time}")
    timed_search_parameters = set_search_params_modify_timestamp(
        search_parameters,
        last_search_time,
    )
    last_search_time = datetime.utcnow()
    ldap_connection.search(**timed_search_parameters)

    if not ldap_connection.response:
        return [], last_search_time

    last_events = []
    responses = apply_discriminator(ldap_connection.response, context)
    for event in responses:
        if event.get("type") != "searchResEntry":
            continue
        # We require modifyTimeStamp to determine if the event is duplicate
        if "modifyTimeStamp" not in event.get("attributes", {}):
            logger.warning("'modifyTimeStamp' not found in event['attributes']")
            continue
        if event in events_to_ignore:
            # Some events get detected twice, because LDAP's >= filter
            # does not quite work with millisecond precision.
            #
            # For example: When modifyTimeStamp == 20230307120826.0Z:
            # We get a hit for the following search filters:
            # - (modifyTimestamp>=20230307120825.256-0000)
            # - (modifyTimestamp>=20230307120826.341-0000)
            #
            # Even though you would expect the second one not to match
            logger.info(f"Ignored duplicate event: {event}")
            continue
        callback(event)
        last_events.append(event)
    return last_events, last_search_time


def _poller(
    context: Context,
    search_parameters: dict,
    callback: Callable,
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
    seeded_poller = partial(
        _poll,
        context=context,
        search_parameters=search_parameters,
        callback=callback,
    )

    last_search_time = init_search_time
    events_to_ignore: list[Any] = []
    while True:
        events_to_ignore, last_search_time = seeded_poller(
            events_to_ignore=events_to_ignore, last_search_time=last_search_time
        )
        time.sleep(poll_time)


def set_search_params_modify_timestamp(search_parameters: dict, timestamp: datetime):
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
    checksum = [ou_to_check.endswith(ou) for ou in list_of_ous]
    if sum(checksum) == 0:
        raise ValueError(f"{ou_to_check} is not in {list_of_ous}")

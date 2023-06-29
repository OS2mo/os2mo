# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=too-few-public-methods
"""Settings handling."""
from typing import List
from typing import Literal

from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import AmqpDsn
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import ConstrainedList
from pydantic import Field
from pydantic import parse_obj_as
from pydantic import SecretStr
from ramqp.config import ConnectionSettings as AMQPConnectionSettings


class ServerConfig(BaseModel):
    """Settings model for domain controllers."""

    class Config:
        """Settings are frozen."""

        frozen = True

    host: str = Field(..., description="Hostname / IP to establish connection with")
    port: int | None = Field(
        None,
        description=(
            "Port to utilize when establishing a connection. Defaults to 636 for SSL"
            " and 389 for non-SSL"
        ),
    )
    use_ssl: bool = Field(False, description="Whether to establish a SSL connection")
    insecure: bool = Field(False, description="Whether to verify SSL certificates")
    timeout: int = Field(5, description="Number of seconds to wait for connection")


class ServerList(ConstrainedList):
    """Constrainted list for domain controllers."""

    min_items = 1
    unique_items = True

    item_type = ServerConfig
    __args__ = (ServerConfig,)


class InternalAMQPConnectionSettings(AMQPConnectionSettings):
    exchange = "ldap_ie_internal"
    queue_prefix = "ldap_ie_internal"
    prefetch_count = 1  # MO cannot handle too many requests
    url: AmqpDsn = parse_obj_as(AmqpDsn, "amqp://guest:guest@msg_broker")


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    internal_amqp: InternalAMQPConnectionSettings = Field(
        default_factory=InternalAMQPConnectionSettings,
        description="Internal amqp settings",
    )

    fastramqpi: FastRAMQPISettings = Field(
        default_factory=FastRAMQPISettings, description="FastRAMQPI settings"
    )

    amqp_url: AmqpDsn = parse_obj_as(AmqpDsn, "amqp://guest:guest@msg_broker")
    amqp_exchange: str = "os2mo"
    listen_to_changes_in_mo: bool = Field(
        True, description="Whether to write to AD, when changes in MO are registered"
    )

    listen_to_changes_in_ldap: bool = Field(
        True, description="Whether to write to MO, when changes in LDAP are registered"
    )

    ldap_controllers: ServerList = Field(
        ..., description="List of domain controllers to query"
    )
    ldap_domain: str = Field(
        ..., description="Domain to use when authenticating with the domain controller"
    )
    ldap_user: str = Field(
        "os2mo",
        description="Username to use when authenticating with the domain controller",
    )
    ldap_password: SecretStr = Field(
        ...,
        description="Password to use when authenticating with the domain controller",
    )
    ldap_search_base: str = Field(
        ..., description="Search base to utilize for all LDAP requests"
    )
    ldap_ous_to_search_in: List[str] = Field(
        [""],
        description=(
            "List of OUs to search in. If this contains an empty string; "
            "Searches in all OUs in the search base"
        ),
    )
    ldap_ous_to_write_to: List[str] = Field(
        [""],
        description=(
            "List of OUs to write to. If this contains an empty string; "
            "Writes to all OUs in the search base"
        ),
    )
    ldap_ou_for_new_users: str = Field(
        "", description="OU to create new users in. For example 'OU=Test'"
    )

    mo_url: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://mo-service:5000"),
        description="Base URL for OS2mo.",
    )

    client_id: str = Field("bruce", description="Client ID for OIDC client.")
    client_secret: SecretStr = Field(..., description="Client Secret for OIDC client.")
    auth_server: AnyHttpUrl = Field(
        parse_obj_as(AnyHttpUrl, "http://keycloak-service:8080/auth"),
        description="Base URL for OIDC server (Keycloak).",
    )
    auth_realm: str = Field("mo", description="Realm to authenticate against")

    graphql_timeout: int = 120

    admin_password: SecretStr = Field(
        ...,
        description="Password to use when authenticating to FastAPI docs",
    )
    authentication_secret: SecretStr = Field(
        ...,
        description="secret key for FastAPI docs login manager",
    )

    default_org_unit_type: str = Field(
        ..., description="Type to set onto imported organization units"
    )

    default_org_unit_level: str = Field(
        ..., description="Level to set onto imported organization units"
    )

    token_expiry_time: float = Field(
        8, description="Time in hours until a FastAPI auth token expires"
    )

    org_unit_path_string_separator: str = Field(
        "\\", description="separator for full paths to org units in LDAP"
    )

    poll_time: float = Field(
        5, description="Seconds between calls to LDAP to search for updates"
    )

    imported_org_unit_tag: str = Field(
        "IMPORTED FROM LDAP: ",
        description="Tag which is added to all imported org-units",
    )

    check_alleroed_sd_number: bool = Field(
        False,
        description=(
            "Check that an SD-employee number does not start with 9, "
            "before writing to LDAP"
        ),
    )

    it_user_to_check: str = Field(
        "",
        description=(
            "Check that an employee has an it-user with this user_key "
            "before writing to LDAP"
        ),
    )

    discriminator_function: Literal["exclude", "include", None] = Field(
        None,
        description="The type of discriminator function, either include or exclude",
    )

    discriminator_field: str | None = Field(
        None, description="The field to look for discriminator values in"
    )

    discriminator_values: List[str] = Field(
        [], description="The values used for discrimination"
    )

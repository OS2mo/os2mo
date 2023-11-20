# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=too-few-public-methods
"""Settings handling."""
from typing import Literal

from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import AnyHttpUrl
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import ConstrainedList
from pydantic import Field
from pydantic import parse_obj_as
from pydantic import PositiveInt
from pydantic import SecretStr
from ramqp.config import AMQPConnectionSettings


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


class ExternalAMQPConnectionSettings(AMQPConnectionSettings):
    queue_prefix = "ldap_ie"
    prefetch_count: int = 1  # MO cannot handle too many requests


class FastFAMQPIApplicationSettings(FastRAMQPISettings):
    mo_graphql_version: PositiveInt = 7
    amqp: ExternalAMQPConnectionSettings


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    internal_amqp: InternalAMQPConnectionSettings = Field(
        default_factory=InternalAMQPConnectionSettings,  # type: ignore
        description="Internal amqp settings",
    )

    fastramqpi: FastFAMQPIApplicationSettings

    listen_to_changes_in_mo: bool = Field(
        True, description="Whether to write to AD, when changes in MO are registered"
    )

    listen_to_changes_in_ldap: bool = Field(
        True, description="Whether to write to MO, when changes in LDAP are registered"
    )

    add_objects_to_ldap: bool = Field(
        True,
        description=(
            "If True: Adds new objects to LDAP "
            "when an object is in MO but not in LDAP. "
            "If False: Only modifies existing objects."
        ),
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
    ldap_ous_to_search_in: list[str] = Field(
        [""],
        description=(
            "List of OUs to search in. If this contains an empty string; "
            "Searches in all OUs in the search base"
        ),
    )
    ldap_ous_to_write_to: list[str] = Field(
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

    default_org_unit_type: str = Field(
        ..., description="Type to set onto imported organization units"
    )

    default_org_unit_level: str = Field(
        ..., description="Level to set onto imported organization units"
    )

    org_unit_path_string_separator: str = Field(
        "\\", description="separator for full paths to org units in LDAP"
    )

    poll_time: float = Field(
        5, description="Seconds between calls to LDAP to search for updates"
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

    check_holstebro_ou_issue_57426: list[str] = Field(
        [],
        description="Check that OU is below or equal one of these, see #57426",
    )

    discriminator_function: Literal["exclude", "include", None] = Field(
        None,
        description="The type of discriminator function, either include or exclude",
    )

    discriminator_field: str | None = Field(
        None, description="The field to look for discriminator values in"
    )

    discriminator_values: list[str] = Field(
        [], description="The values used for discrimination"
    )

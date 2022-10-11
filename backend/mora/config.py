# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os
from enum import Enum
from functools import lru_cache
from typing import Any

from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import Field
from pydantic import root_validator
from pydantic import validator
from pydantic.types import DirectoryPath
from pydantic.types import FilePath
from pydantic.types import PositiveInt
from pydantic.types import UUID
from structlog import get_logger

logger = get_logger()


class NavLink(BaseSettings):
    href: AnyHttpUrl
    text: str


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ServicePlatformenSettings(BaseSettings):
    sp_service_uuid: UUID
    sp_agreement_uuid: UUID
    sp_municipality_uuid: UUID
    sp_system_uuid: UUID
    sp_certificate_path: FilePath
    sp_production: bool = False

    @validator("sp_certificate_path")
    def validate_certificate_not_empty(cls, v):
        if not v.stat().st_size:
            raise ValueError("Serviceplatformen certificate can not be empty")
        return v


class FileSystemSettings(BaseSettings):
    query_export_dir: DirectoryPath = "/queries"
    query_insight_dir: DirectoryPath | None = None


class Settings(BaseSettings):
    """
    These settings can be overwritten by environment variables
    The environement variable name is the upper-cased version of the variable name below
    E.g. LORA_URL == lora_url
    """

    commit_tag: str | None
    commit_sha: str | None
    lora_url: AnyHttpUrl = "http://mox/"
    enable_internal_lora: bool = False

    # Misc OS2mo settings
    environment: Environment = Environment.PRODUCTION
    os2mo_log_level: str = "WARNING"
    enable_cors: bool = False
    navlinks: list[NavLink] = []

    # File Store settings
    file_storage: str = "noop"
    filesystem_settings: FileSystemSettings | None = None

    @root_validator
    def check_filesystem_settings(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("file_storage") != "filesystem":
            return values

        values["filesystem_settings"] = FileSystemSettings()
        return values

    # Enable auth-endpoints and auth
    os2mo_auth: bool = True
    # When graphql_rbac is disabled, it is in fact still enabled for graphql mutators.
    # This is due to a hotfix for a security security vulnerability in the orgviewer.
    # This hotfix will be removed again later, once the security issues has been fixed.
    graphql_rbac: bool = False

    log_level: LogLevel = LogLevel.INFO

    @root_validator
    def graphql_rbac_dependencies(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not values["graphql_rbac"]:
            return values

        dependencies = {"os2mo_auth", "keycloak_rbac_enabled"}
        for dependency in dependencies:
            if not values[dependency]:
                raise ValueError(
                    f"'{dependency}' must be true when graphql_rbac is enabled"
                )
        return values

    # airgapped options
    enable_dar: bool = True
    enable_sp: bool = True

    # `dummy_mode` is different from airgapped although it also stops MO from
    # making some Internet connections. For now, the difference is that DAR
    # still works in dummy mode and SP generates fake date. With
    # `enable_sp=False` no fake data is generated.
    dummy_mode: bool = False

    # Legacy auth
    os2mo_legacy_session_support: bool = False
    session_db_user = "sessions"
    session_db_password: str | None
    session_db_host = "mox-db"
    session_db_port = "5432"
    session_db_name = "sessions"

    # Bulked LoRa DataLoader fetching
    bulked_fetch: bool = True

    # Endpoint switches
    # Enable testing endpoints
    testcafe_enable: bool = True
    # Serve frontend
    statics_enable: bool = False
    # GraphQL settings
    graphql_enable: bool = True
    graphiql_enable: bool = False

    # HTTP Trigger settings
    http_endpoints: list[str] | None
    fetch_trigger_timeout: int = 5
    run_trigger_timeout: int = 5

    # HTTPX
    httpx_timeout: PositiveInt = 60

    # AMQP settings
    amqp_enable: bool = False
    # AMQP connection settings are extracted from environment variables by the RAMQP
    # library directly.
    sp_settings: ServicePlatformenSettings | None = None

    @root_validator
    def check_sp_configuration(cls, values: dict[str, Any]) -> dict[str, Any]:
        # If SP is not enabled, no reason to check configuration
        if not values.get("enable_sp"):
            return values
        # If SP is in dummy mode, no reason to check configuration
        # NOTE: This code is kinda similar to is_dummy_mode
        if values.get("environment") is not Environment.PRODUCTION:
            return values
        if values.get("dummy_mode"):
            return values

        values["sp_settings"] = ServicePlatformenSettings()
        return values

    # Keycloak settings
    keycloak_schema: str = "https"
    keycloak_host: str = "keycloak"
    keycloak_port: int = 443
    keycloak_realm: str = "mo"
    keycloak_mo_client: str = "mo-frontend"
    keycloak_signing_alg: str = "RS256"
    keycloak_verify_audience: bool = True
    keycloak_auth_server_url: AnyHttpUrl = "http://localhost:8081/auth/"
    keycloak_ssl_required: str = "external"
    keycloak_rbac_enabled: bool = False

    # Lora client
    lora_client_id: str = "mo"
    lora_client_secret: str | None
    lora_auth_realm: str = "lora"
    lora_auth_server: AnyHttpUrl = "http://keycloak:8080/auth"

    @root_validator
    def show_owners_must_be_true_if_rbac_is_enabled(
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        if values["keycloak_rbac_enabled"]:
            if not values["confdb_show_owner"]:
                raise ValueError(
                    "'confdb_show_owner' must be true when RBAC is enabled"
                )
        return values

    # ConfDB settings
    confdb_show_roles: bool = True
    confdb_show_kle: bool = False
    confdb_show_user_key: bool = True
    confdb_show_location: bool = True
    confdb_show_time_planning: bool = False
    confdb_show_level: bool = True
    confdb_show_primary_engagement: bool = False
    confdb_show_primary_association: bool = False

    # Show the refresh button for org-units
    confdb_show_org_unit_button: bool = False
    confdb_inherit_manager: bool = True
    confdb_association_dynamic_facets: str = ""
    confdb_substitute_roles: str = ""
    confdb_show_cpr_no: bool = Field(
        True, description="Make CPR number visible under the Employee tab"
    )
    confdb_show_user_key_in_search: bool = False
    confdb_extension_field_ui_labels: str = ""
    confdb_show_engagement_hyperlink: bool = False
    confdb_show_seniority: bool = False
    confdb_show_owner: bool = False
    confdb_show_custom_logo: str = ""

    # Autocomplete: use new API? Requires LoRa 1.13 or later.
    # See #38239.
    confdb_autocomplete_use_new_api: bool = False
    # List of class UUIDs whose title and value will be displayed for each
    # matching employee.
    confdb_autocomplete_attrs_employee: list[UUID] | None
    # List of class UUIDs whose title and value will be displayed for each
    # matching organisation unit.
    confdb_autocomplete_attrs_orgunit: list[UUID] | None

    # MO allows "fictitious" birthdates in CPR numbers, if this is set to False
    cpr_validate_birthdate: bool = True

    # MO UI displays an "IT associations" tab for employees, if this is set to True
    show_it_associations_tab: bool = False

    # MO displays access address in organiasation-address-autocomplete-endpoint.
    dar_address_autocomplete_includes_access_addresses: bool = False

    def is_production(self) -> bool:
        """Return whether we are running in a production environment."""
        return self.environment is Environment.PRODUCTION

    def is_dummy_mode(self) -> bool:
        """Return whether serviceplatform is in dummy mode."""
        # Force dummy-mode during tests and development,
        # but make it configurable in production.
        if not self.is_production():
            return True
        return self.dummy_mode

    def is_under_test(self) -> bool:
        return os.environ.get("PYTEST_RUNNING") is not None


@lru_cache
def get_settings(*args, **kwargs) -> Settings:
    return Settings(*args, **kwargs)


def get_public_settings() -> set[str]:
    """Set of settings keys that are exposed to the world.

    Returns:
        Set of settings keys.
    """
    various_keys = {
        "commit_tag",
        "commit_sha",
        "environment",
        "dummy_mode",
        "navlinks",
        "show_it_associations_tab",
        "keycloak_rbac_enabled",
        "file_storage",
    }
    confdb_keys = filter(
        lambda key: key.startswith("confdb_"), Settings.__fields__.keys()
    )
    return set.union(various_keys, confdb_keys)

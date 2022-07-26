# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os
from enum import Enum
from functools import lru_cache
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import Field
from pydantic import root_validator
from pydantic.types import DirectoryPath
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


class Settings(BaseSettings):
    """
    These settings can be overwritten by environment variables
    The environement variable name is the upper-cased version of the variable name below
    E.g. LORA_URL == lora_url
    """

    commit_tag: Optional[str]
    commit_sha: Optional[str]
    lora_url: AnyHttpUrl = "http://mox/"

    # Misc OS2mo settings
    environment: Environment = Environment.PRODUCTION
    os2mo_log_level: str = "WARNING"
    enable_cors: bool = False
    query_export_dir: DirectoryPath = "/queries"
    query_insight_dir: Optional[DirectoryPath] = None
    navlinks: List[NavLink] = []
    # Enable auth-endpoints and auth
    os2mo_auth: bool = True

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
    session_db_password: Optional[str]
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
    http_endpoints: Optional[List[str]]
    fetch_trigger_timeout: int = 5
    run_trigger_timeout: int = 5

    # HTTPX
    httpx_timeout: PositiveInt = 60

    # AMQP settings
    amqp_enable: bool = False
    # AMQP connection settings are extracted from environment variables by the RAMQP
    # library directly.

    # Serviceplatform settings
    sp_service_uuid: Optional[UUID]
    sp_agreement_uuid: Optional[UUID]
    sp_municipality_uuid: Optional[UUID]
    sp_system_uuid: Optional[UUID]
    sp_certificate_path: Optional[str]
    sp_production: Optional[bool]

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
    lora_client_secret: Optional[str]
    lora_auth_realm: str = "lora"
    lora_auth_server: AnyHttpUrl = "http://keycloak:8080/auth"

    @root_validator
    def show_owners_must_be_true_if_rbac_is_enabled(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
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
    confdb_autocomplete_attrs_employee: Optional[List[UUID]]
    # List of class UUIDs whose title and value will be displayed for each
    # matching organisation unit.
    confdb_autocomplete_attrs_orgunit: Optional[List[UUID]]

    # MO allows "fictitious" birthdates in CPR numbers, if this is set to False
    cpr_validate_birthdate: bool = True

    # MO UI displays an "IT associations" tab for employees, if this is set to True
    show_it_associations_tab: bool = False

    def is_production(self) -> bool:
        """Return whether we are running in a production environment"""
        return self.environment is Environment.PRODUCTION

    def is_under_test(self) -> bool:
        return os.environ.get("PYTEST_RUNNING") is not None


@lru_cache()
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
    }
    confdb_keys = filter(
        lambda key: key.startswith("confdb_"), Settings.__fields__.keys()
    )
    return set.union(various_keys, confdb_keys)

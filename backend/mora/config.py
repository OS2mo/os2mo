# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import os
from enum import Enum
from functools import lru_cache
from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import root_validator
from pydantic.types import UUID
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class NavLink(BaseSettings):
    href: AnyHttpUrl
    text: str


class Environment(str, Enum):
    DEVELOPMENT = 'development'
    TESTING = 'testing'
    PRODUCTION = 'production'


class Settings(BaseSettings):
    """
    These settings can be overwritten by environment variables
    The environement variable name is the upper-cased version of the variable name below
    E.g. LORA_URL == lora_url
    """
    lora_url: AnyHttpUrl = "http://mox/"

    # Misc OS2mo settings
    environment: Environment = Environment.PRODUCTION
    os2mo_log_level: str = "WARNING"
    enable_cors: bool = False
    dummy_mode: bool = False
    query_export_dir: Optional[str] = "/queries"
    navlinks: List[NavLink] = []
    os2mo_auth: bool = True

    # HTTP Trigger settings
    http_endpoints: Optional[List[str]]
    fetch_trigger_timeout: int = 5
    run_trigger_timeout: int = 5

    # AMQP settings
    amqp_enable: bool = False
    amqp_host: str = "msg_broker"
    amqp_port: int = 5672
    amqp_os2mo_exchange: str = "os2mo"

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
    keycloak_mo_client: str = "mo"
    keycloak_signing_alg: str = "RS256"
    keycloak_auth_server_url: AnyHttpUrl = "http://localhost:8081/auth/"
    keycloak_ssl_required: str = "external"
    keycloak_rbac_enabled: bool = False

    @root_validator
    def show_owners_must_be_true_if_rbac_is_enabled(
            cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        if values['keycloak_rbac_enabled']:
            if not values['confdb_show_owner']:
                raise ValueError(
                    "'confdb_show_owner' must be true when RBAC is enabled"
                )
        return values

    # ConfDB database settings
    # Use configuration DB for get_configuration endpoint
    conf_db_use: bool = True
    conf_db_name: str = "mora"
    conf_db_user: str = "mora"
    conf_db_password: Optional[str]
    conf_db_host: str = "mox-db"
    conf_db_port: str = "5432"
    conf_db_sslmode: Optional[str]

    @root_validator
    def conf_db_password_maybe_required(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # If conf_db_password only required if conf_db is used
        if values["conf_db_use"]:
            if "conf_db_password" not in values:
                raise ValueError("conf_db_password not set")
            if values["conf_db_password"] is None:
                raise ValueError("conf_db_password is None")
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
    confdb_show_org_unit_button: bool = False
    confdb_inherit_manager: bool = True
    confdb_association_dynamic_facets: str = ''
    confdb_substitute_roles: str = ''
    confdb_show_cpr_no: bool = True
    confdb_show_user_key_in_search: bool = False
    confdb_extension_field_ui_labels: str = ''
    confdb_show_engagement_hyperlink: bool = False
    confdb_show_seniority: bool = False
    confdb_show_owner: bool = False

    # Autocomplete: use new API? Requires LoRa 1.13 or later.
    # See #38239.
    confdb_autocomplete_use_new_api: bool = False
    # List of class UUIDs whose title and value will be displayed for each
    # matching employee.
    confdb_autocomplete_attrs_employee: Optional[List[UUID]]
    # List of class UUIDs whose title and value will be displayed for each
    # matching organisation unit.
    confdb_autocomplete_attrs_orgunit: Optional[List[UUID]]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def is_production() -> bool:
    """Return whether we are running in a production environment"""
    return get_settings().environment is Environment.PRODUCTION


def is_under_test() -> bool:
    return os.environ.get('PYTEST_RUNNING', False)

# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from enum import Enum
from functools import lru_cache
from typing import List
from typing import Optional

from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic.types import UUID


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

    lora_url: AnyHttpUrl = "http://mox/"

    # Config database settings
    conf_db_name: str = "mora"
    conf_db_user: str = "mora"
    conf_db_password: str
    conf_db_host: str = "mox-db"
    conf_db_port: str = "5432"

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
    amqp_host: Optional[str]
    amqp_port: Optional[str]
    amqp_os2mo_exchange: Optional[str]

    # Serviceplatform settings
    sp_service_uuid: Optional[UUID]
    sp_agreement_uuid: Optional[UUID]
    sp_municipality_uuid: Optional[UUID]
    sp_system_uuid: Optional[UUID]
    sp_certificate_path: Optional[str]
    sp_production: Optional[bool]

    # Keycloak
    keycloak_schema: str = "https"
    keycloak_host: str = "keycloak"
    keycloak_port: int = 443
    keycloak_realm: str = "mo"
    keycloak_signing_alg: str = "RS256"

    # MO allows "fictitious" birthdates in CPR numbers, if this is set to False
    cpr_validate_birthdate: bool = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def is_production() -> bool:
    """Return whether we are running in a production environment"""
    return get_settings().environment is Environment.PRODUCTION

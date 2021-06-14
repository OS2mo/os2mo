from functools import lru_cache
from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl
from pydantic.types import UUID
from typing import List, Optional


class NavLink(BaseSettings):
    href: AnyHttpUrl
    text: str


class Settings(BaseSettings):
    """
    These settings can be overwritten by environment variables
    The environement variable name is the upper-cased version of the variable name below
    E.g. LORA_URL == lora_url
    """
    lora_url: AnyHttpUrl

    # Config database settings
    conf_db_name: str
    conf_db_user: str
    conf_db_password: str
    conf_db_host: str
    conf_db_port: str

    # Misc OS2mo settings
    environment: str = "production"
    os2mo_log_level: str = "WARNING"
    enable_cors: bool = False
    dummy_mode: bool = False
    query_export_dir: Optional[str]
    navlinks: List[NavLink] = []

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


@lru_cache()
def get_settings() -> Settings:
    return Settings()

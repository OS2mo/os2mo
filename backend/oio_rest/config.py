# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    These settings can be overwritten by environment variables
    The environement variable name is the upper-cased version of the variable name below
    E.g. DB_NAME == db_name
    """

    db_name: str = "mox"
    db_user: str = "mox"
    db_password: str | None
    db_host: str = "mox-db"
    db_port: str = "5432"
    db_sslmode: str | None

    # The log level for the Python application
    lora_log_level: str = "WARNING"

    # If enabled, uses alternative search implementation
    quick_search: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()

# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
# pylint: disable=too-few-public-methods
"""Settings handling."""
from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import AmqpDsn
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import ConstrainedList
from pydantic import Field
from pydantic import parse_obj_as
from pydantic import SecretStr


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


class Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: FastRAMQPISettings = Field(
        default_factory=FastRAMQPISettings, description="FastRAMQPI settings"
    )

    amqp_url: AmqpDsn = parse_obj_as(AmqpDsn, "amqp://guest:guest@localhost:5672")
    amqp_exchange: str = "os2mo"

    ad_controllers: ServerList = Field(
        ..., description="List of domain controllers to query"
    )
    ad_domain: str = Field(
        ..., description="Domain to use when authenticating with the domain controller"
    )
    ad_user: str = Field(
        "os2mo",
        description="Username to use when authenticating with the domain controller",
    )
    ad_password: SecretStr = Field(
        ...,
        description="Password to use when authenticating with the domain controller",
    )
    ad_search_base: str = Field(
        ..., description="Search base to utilize for all AD requests"
    )

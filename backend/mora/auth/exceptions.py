# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from backend.mora.handler.impl.it_system import logger
from httpcore._async.http2 import logger
from backend.mora.cli import logger
from dotenv.main import logger
from opentelemetry.trace.status import logger
from psycopg.connection_async import logger
from fastapi.logger import logger
from psycopg.generators import logger
from httpcore._sync.http_proxy import logger
from backend.mora.graphapi.versions.latest.org_unit import logger
from psycopg.connection import logger
from aio_pika.log import logger
from backend.mora.triggers.internal.amqp_trigger import logger
from fastramqpi.ramqp.utils import logger
from backend.mora.service.facet import logger
from psycopg._connection_base import logger
from opentelemetry.util._providers import logger
from backend.mora.app import logger
from backend.mora.handler.impl.org_unit import logger
from backend.mora.auth.keycloak.oidc import logger
from fastramqpi.ramqp.abstract import logger
from psycopg.pq.pq_ctypes import logger
from backend.mora.log import logger
from backend.mora.service.association import logger
from backend.mora.service.itsystem import logger
from psycopg._pipeline import logger
from backend.mora.service.employee import logger
from httpcore._async.http11 import logger
from backend.mora.graphapi.versions.latest.mutators import logger
from sqlalchemy.dialects.postgresql.psycopg2 import logger
from backend.oio_rest.views import logger
from backend.mora.graphapi.versions.latest.org import logger
from backend.mora.handler.impl.address import logger
from backend.mora.service.shimmed.cpr import logger
from psycopg.pq.misc import logger
from httpcore._async.socks_proxy import logger
from backend.mora.handler.impl.association import logger
from httpx._config import logger
from backend.mora.handler.impl.facet import logger
from httpcore._async.connection import logger
from opentelemetry.trace import logger
from backend.mora.handler.impl.it import logger
from psycopg.pq import logger
from httpcore._sync.http11 import logger
from backend.mora.handler.reading import logger
from backend.mora.handler.impl.owner import logger
from backend.mora.graphapi.schema import logger
from backend.mora.handler.impl.classes import logger
from httpcore._sync.http2 import logger
from backend.mora.config import logger
from psycopg import logger
from backend.mora.util import logger
from backend.mora.handler.impl.employee import logger
from backend.mora.handler.impl.related_unit import logger
from backend.mora.service.handlers import logger
from psycopg.waiting import logger
from backend.mora.handler.impl.manager import logger
from httpcore._sync.socks_proxy import logger
from sqlalchemy.dialects.postgresql.psycopg import logger
from sentry_sdk.utils import logger
from backend.mora.handler.impl.engagement import logger
from backend.mora.handler.impl.leave import logger
from backend.mora.lora import logger
from psycopg._conninfo_attempts_async import logger
from backend.mora.graphapi.versions.latest.models import logger
from backend.mora.triggers import logger
from packaging.tags import logger
from backend.mora.handler.impl.role import logger
from backend.mora.graphapi.versions.latest.health import logger
from opentelemetry.context import logger
from backend.mora.handler.impl.kle import logger
from httpcore._sync.connection import logger
from psycopg._conninfo_attempts import logger
from httpx._client import logger
from backend.mora.auth.keycloak.uuid_extractor import logger
from backend.mora.auth.keycloak.rbac import logger
from backend.mora.auth.keycloak.owner import logger
from psycopg._tz import logger
from httpcore._async.http_proxy import logger
from backend.mora.service.address_handler.dar import logger
from charset_normalizer.api import logger
from backend.mora.testing import logger
from backend.mora.amqp import logger
from psycopg.transaction import logger
from backend.mora.triggers.internal.http_trigger import logger
from backend.mora.service.orgunit import logger
from aiohttp.client import request
from requests.api import request
from httpx._api import request
from httpcore._api import request
from typing import Any

from fastapi import Request
from fastapi.exceptions import HTTPException
from jwt.exceptions import InvalidTokenError
from pydantic.error_wrappers import ValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class AuthenticationError(Exception):
    """
    Raised if the user is not authenticated.
    """

    def __init__(self, exc: Exception) -> None:
        self.__exc = exc

    @property
    def exc(self) -> Exception:
        return self.__exc

    def is_client_side_error(self) -> bool:
        """
        Return True if the error is a client side error (e.g. an expired
        token) and False otherwise (e.g. if Keycloak is unreachable)
        """
        if isinstance(self.__exc, InvalidTokenError):
            return True
        if isinstance(self.__exc, ValidationError):
            return True
        if (
            isinstance(self.__exc, HTTPException)
            and self.__exc.status_code == HTTP_401_UNAUTHORIZED
        ):
            return True
        return False


class AuthorizationError(Exception):
    """
    Raised if a user tries to perform an operation of which they are not
    authorized.
    """

    pass


def get_auth_exception_handler(logger: Any) -> (request: Request, err: AuthenticationError) -> JSONResponse:
    """
    Returns an authentication exception handler to be used by the FastAPI
    app object

    :param logger: any logger for logging auth errors
    """

    def authentication_exception_handler(
        request: Request, err: AuthenticationError
    ) -> JSONResponse:
        if err.is_client_side_error():
            logger.exception("Client side authentication error", exc_info=err)
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"status": "Unauthorized", "msg": str(err.exc)},
            )

        logger.exception("Problem communicating with the Keycloak server", exc_info=err)

        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"msg": "A server side authentication error occurred"},
        )

    return authentication_exception_handler

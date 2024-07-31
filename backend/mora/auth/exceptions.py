# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from fastapi import Request
from fastapi.exceptions import HTTPException
from jwt.exceptions import InvalidTokenError
from pydantic.v1.error_wrappers import ValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR


class AuthenticationError(Exception):
    """
    Raised if the user is not authenticated.
    """

    def __init__(self, exc: Exception):
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


def get_auth_exception_handler(logger: Any):
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

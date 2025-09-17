# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import inspect
import traceback
from enum import Enum
from typing import NoReturn

from fastapi import HTTPException as fastapiHTTPException
from starlette.responses import JSONResponse

from mora import config


class ErrorCodes(Enum):
    """This enumeration describes the possible errors codes returned by
    the application. Each item in the enumeration consists of three
    values:

    * A unique string identifying the code.
    * An integer identifying the HTTP status code returned for the
      error — see :rfc:`2616#section-10`.
    * An human-readable string describing the circumstances of the
      error.

    The special code :py:attr:`mora.exceptions.ErrorCodes.E_UNKNOWN`
    means that an unknown, internal error occurred within the
    application. This is most likely a bug.

    """

    @property
    def description(self):
        return self.value[1]

    @property
    def code(self):
        return self.value[0]

    def __call__(self, *args, **kwargs) -> NoReturn:
        """Raise an :py:class:`HTTPException` for this error code"""
        raise self.to_http_exception(*args, **kwargs)

    def to_http_exception(self, *args, **kwargs) -> "HTTPException":
        return HTTPException(self, *args, **kwargs)

    # Validation errors
    V_MISSING_REQUIRED_VALUE = 400, "Missing required value."
    V_INVALID_VALIDITY = 400, "Invalid validity."
    V_MISSING_START_DATE = 400, "Missing start date."
    V_END_BEFORE_START = 400, "End date is before start date."
    V_EXISTING_CPR = 409, "Person with CPR number already exists."
    V_NO_PERSON_FOR_CPR = 404, "No person found for given CPR number."
    V_CPR_NOT_VALID = 400, "Not a valid CPR number."
    V_ORG_UNIT_MOVE_TO_CHILD = (
        400,
        "Org unit cannot be moved to one of its own child units",
    )
    V_TERMINATE_UNIT_WITH_CHILDREN_AND_ROLES = (
        400,
        "Cannot terminate unit with active children and roles.",
    )
    V_TERMINATE_UNIT_WITH_CHILDREN = 400, "Cannot terminate unit with active children."
    V_TERMINATE_UNIT_WITH_ROLES = 400, "Cannot terminate unit with active roles."
    V_TERMINATE_UNIT_WITH_ADDRESSES = (
        400,
        "Cannot terminate unit with active addresses.",
    )
    V_DATE_OUTSIDE_ORG_UNIT_RANGE = (
        400,
        "Date range exceeds validity range of associated org unit.",
    )
    V_DATE_OUTSIDE_EMPL_RANGE = (
        400,
        "Date range exceeds validity range of associated employee.",
    )
    V_CANNOT_MOVE_UNIT_TO_ROOT_LEVEL = (
        400,
        "Moving an org unit to the root level is not allowed",
    )
    V_MORE_THAN_ONE_ASSOCIATION = (
        400,
        "The employee already has an active association with the given org unit.",
    )
    V_MORE_THAN_ONE_PRIMARY = (
        400,
        "Employee already has another active and primary function.",
    )
    V_NO_ACTIVE_ENGAGEMENT = 400, "Employee must have an active engagement."
    V_UNIT_OUTSIDE_ORG = (
        400,
        "Unit belongs to an organisation different from the current one.",
    )
    V_PARENT_NOT_FOUND = 404, "Corresponding parent unit or organisation not found."
    V_DUPLICATED_RESPONSIBILITY = (
        400,
        "Manager has the same responsibility more than once.",
    )
    V_DUPLICATED_IT_USER = (
        400,
        "Employee has the same IT user more than once",
    )
    V_CANNOT_SUBSTITUTE_SELF = 400, "Cannot substitute for oneself"
    V_INVALID_ADDRESS_DAR = 400, "Invalid address"
    V_INVALID_ADDRESS_EAN = 400, "Invalid EAN"
    V_INVALID_ADDRESS_EMAIL = 400, "Invalid email"
    V_INVALID_ADDRESS_PNUMBER = 400, "Invalid P-number"
    V_INVALID_ADDRESS_PHONE = 400, "Invalid phone number"
    V_INVALID_ADDRESS_WWW = 400, "Invalid web address"
    V_INVALID_ADDRESS_UUID = 400, "Invalid UUID"

    # Input errors
    E_ORG_UNIT_NOT_FOUND = 404, "Org unit not found."
    E_CLASS_NOT_FOUND = 404, "Class not found."
    E_USER_NOT_FOUND = 404, "User not found."
    E_UNKNOWN_ROLE_TYPE = 400, "Unknown role type."
    E_INVALID_ROLE_TYPE = 400, "Invalid role type for target operation."
    E_INVALID_TYPE = 400, "Invalid type."
    E_INVALID_UUID = 400, "Invalid UUID."
    E_INVALID_URN = 400, "Invalid URN."
    E_ORIGINAL_ENTRY_NOT_FOUND = 400, "Original entry not found."
    E_NO_LOCAL_MUNICIPALITY = 400, "No local municipality found."
    E_SIZE_MUST_BE_POSITIVE = 400, "Size must be positive."
    E_TOO_MANY_RESULTS = 400, "Amount of results exceeds limit."
    E_RELATED_TO_SELF = 400, "Orgunit cannot be related to itself."

    # Misc
    E_INCONSISTENT_SETTINGS = 400, "Inconsistent global settings."
    E_INVALID_INPUT = 400, "Invalid input."
    E_UNAUTHORIZED = 401, "Unauthorized."
    E_FORBIDDEN = 403, "Forbidden."
    E_CONNECTION_FAILED = 500, "Connection failed."
    E_SAML_AUTH_ERROR = 500, "Internal auth error."
    E_INTERNAL_ERROR = 500, "Internal error."
    E_NOT_FOUND = 404, "Not found."
    E_ALREADY_EXISTS = 409, "File already exists."
    E_NO_SUCH_ENDPOINT = 404, "No such endpoint."
    E_UNKNOWN = 500, "Unknown Error."
    E_DIR_NOT_FOUND = 500, "Directory does not exist."
    E_SP_SSL_ERROR = 500, "SSL Error connecting to SP"
    E_ORG_UNCONFIGURED = 400, "Organisation has not been configured"
    E_ORG_CONFIG_BAD = 400, "Organisation configuration differs from database"
    E_ORG_TOO_MANY = 400, "Too many organisations in lora, max one allowed"
    E_ORG_NOT_ALLOWED = 400, "Organisation is not allowed"
    E_INTEGRATION_ERROR = 400, "Integration Error"


class HTTPException(fastapiHTTPException):
    key = ErrorCodes.E_UNKNOWN

    @property
    def code(self) -> ErrorCodes:  # pragma: no cover
        return self.key.code

    # Added to have pre 0.29.0 Starlette HTTPException behavior
    __str__ = Exception.__str__

    def __init__(
        self,
        error_key: ErrorCodes | None = None,
        message: str | None = None,
        *,
        cause=None,
        **extras,
    ) -> None:
        if error_key is not None:
            self.key = error_key

        self.traceback: str | None = None
        self.stack: str | None = None

        body = {
            "error": True,
            "description": message or self.key.description,
            "status": self.key.code,
            "error_key": self.key.name,
            **extras,
        }

        settings = config.get_settings()
        if not settings.is_production():
            if cause is None:
                cause = self.__cause__ or self
            # just for debugging, remove or change as needed:
            frame = inspect.currentframe()  # CPython only
            # the stacked f_backs are just to leave out our crazy __call__
            # from ErrorCodes of the traceback.
            self.stack = "".join(
                traceback.format_stack(f=frame.f_back.f_back.f_back, limit=15)
            )

        super().__init__(status_code=self.key.code, detail=body)


class ImproperlyConfigured(Exception):
    """MO is somehow improperly configured."""

    pass


def http_exception_to_json_response(exc: fastapiHTTPException) -> JSONResponse:
    """
    introduced to maintain backwards compatibility
    :param exc:
    :param new_status_code:
    :return:
    """
    return JSONResponse(status_code=exc.status_code, content=exc.detail)

#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from enum import Enum


class ErrorCodes(Enum):
    # Validation errors
    V_MISSING_REQUIRED_VALUE = "Missing required value."
    V_INVALID_VALIDITY = "Invalid validity."
    V_MISSING_START_DATE = "Missing start date."
    V_ORIGINAL_REQUIRED = "Original required."
    V_NO_PERSON_FOR_CPR = "No person found for given CPR number."
    V_CPR_NOT_VALID = "Not a valid CPR number."
    V_ORG_UNIT_MOVE_TO_CHILD = "Org unit cannot be moved to one of " \
                               "its own child units"
    V_TERMINATE_UNIT_WITH_CHILDREN_OR_ROLES = "Cannot terminate unit with " \
                                              "active children and roles."
    V_DATE_OUTSIDE_ORG_UNIT_RANGE = "Date range exceeds validity range " \
                                    "of associated org unit."
    V_DATE_OUTSIDE_EMPL_RANGE = "Date range exceeds validity range " \
                                "of associated employee."
    V_CANNOT_MOVE_ROOT_ORG_UNIT = "Moving the root org unit is not allowed"

    # Input errors
    E_ORG_UNIT_NOT_FOUND = "Org unit not found."
    E_USER_NOT_FOUND = "User not found."
    E_UNKNOWN_ROLE_TYPE = "Unknown role type."
    E_INVALID_TYPE = "Invalid type."
    E_INVALID_UUID = "Invalid UUID."
    E_INVALID_URN = "Invalid URN."
    E_ORIGINAL_ENTRY_NOT_FOUND = "Original entry not found."
    E_INVALID_FUNCTION_TYPE = "Invalid function type."
    E_NO_LOCAL_MUNICIPALITY = "No local municipality found."
    E_SIZE_MUST_BE_POSITIVE = "Size must be positive."

    # Misc
    E_INVALID_INPUT = "Invalid input."
    E_UNAUTHORIZED = "Unauthorized."
    E_CONNECTION_FAILED = "Connection failed."
    E_NOT_FOUND = "Not found."
    E_NO_SUCH_ENDPOINT = "No such endpoint."
    E_UNKNOWN_ERROR = "Unknown Error."

#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from enum import Enum


class Error(Enum):
    # Validation errors
    V1 = "Missing required value."
    V2 = "Invalid validity."
    V3 = "Missing start date."
    V4 = "Original required."
    V5 = "No person found for given CPR number."
    V6 = "Not a valid CPR number."
    V7 = "Org unit cannot be moved to one of its own child units"
    V8 = "Cannot terminate unit with active children and roles."
    V9 = "Date range exceeds validity range of associated org unit."
    V10 = "Date range exceeds validity range of associated employee."
    V11 = "Moving the root org unit is not allowed"

    # Input errors
    E10 = "Org unit not found."
    E11 = "User not found."
    E12 = "Unknown role type."
    E31 = "Invalid type."
    E32 = "Invalid UUID."
    E33 = "Invalid URN."
    E34 = "Original entry not found."
    E36 = "Invalid function type."
    E37 = "No local municipality found."
    E38 = "Size must be positive."

    # Misc
    E90000 = "Invalid input."
    E90001 = "Unauthorized."
    E90002 = "Connection failed."
    E90003 = "Not found."
    E90004 = "No such endpoint."
    E99999 = "Unknown Error."

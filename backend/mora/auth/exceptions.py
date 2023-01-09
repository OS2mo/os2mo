# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0


class AuthorizationError(Exception):
    """
    Raised if a user tries to perform an operation of which they are not
    authorized.
    """

    pass

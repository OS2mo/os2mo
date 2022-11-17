# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0


class MultipleObjectsReturnedException(Exception):
    pass


class NoObjectsReturnedException(Exception):
    pass


class CprNoNotFound(Exception):
    pass


class IncorrectMapping(Exception):
    pass

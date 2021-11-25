# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from contextlib import contextmanager

from starlette.datastructures import ImmutableMultiDict


# I'm a singleton


class _QueryArgs:
    def __init__(self):
        self.__query_args: ImmutableMultiDict = ImmutableMultiDict()

    @property
    def args(self) -> ImmutableMultiDict:
        return self.__query_args

    @args.setter
    def args(self, value: ImmutableMultiDict):
        self.__query_args = value

    @contextmanager
    def context_args(self, value: ImmutableMultiDict):
        org = self.args
        self.args = value
        try:
            yield None
        finally:
            self.args = org


current_query = _QueryArgs()

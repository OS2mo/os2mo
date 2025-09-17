# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from alembic.operations import MigrateOperation


class DropFunctionOp(MigrateOperation):
    """Drop a FUNCTION."""

    def __init__(self, function_name, schema=None) -> None:
        self.function_name = function_name
        self.schema = schema

    @classmethod
    def drop_function(cls, operations, function_name, **kw):
        """Issue a "DROP FUNCTION" instruction."""

        op = DropFunctionOp(function_name, **kw)
        return operations.invoke(op)


def drop_function(operations, operation) -> None:
    if operation.schema is not None:
        name = f"{operation.schema}.{operation.function_name}"
    else:
        name = operation.function_name
    operations.execute("DROP FUNCTION %s" % name)

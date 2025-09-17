# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from alembic.operations import MigrateOperation


class CreateSequenceOp(MigrateOperation):
    """Create a SEQUENCE."""

    def __init__(self, sequence_name, schema=None) -> None:
        self.sequence_name = sequence_name
        self.schema = schema

    @classmethod
    def create_sequence(cls, operations, sequence_name, **kw):
        """Issue a "CREATE SEQUENCE" instruction."""

        op = CreateSequenceOp(sequence_name, **kw)
        return operations.invoke(op)

    def reverse(self) -> DropSequenceOp:
        # only needed to support autogenerate
        return DropSequenceOp(self.sequence_name, schema=self.schema)


class DropSequenceOp(MigrateOperation):
    """Drop a SEQUENCE."""

    def __init__(self, sequence_name, schema=None) -> None:
        self.sequence_name = sequence_name
        self.schema = schema

    @classmethod
    def drop_sequence(cls, operations, sequence_name, **kw):
        """Issue a "DROP SEQUENCE" instruction."""

        op = DropSequenceOp(sequence_name, **kw)
        return operations.invoke(op)

    def reverse(self) -> CreateSequenceOp:
        # only needed to support autogenerate
        return CreateSequenceOp(self.sequence_name, schema=self.schema)


def create_sequence(operations, operation) -> None:
    if operation.schema is not None:
        name = f"{operation.schema}.{operation.sequence_name}"
    else:
        name = operation.sequence_name
    operations.execute("CREATE SEQUENCE %s" % name)


def drop_sequence(operations, operation) -> None:
    if operation.schema is not None:
        name = f"{operation.schema}.{operation.sequence_name}"
    else:
        name = operation.sequence_name
    operations.execute("DROP SEQUENCE %s" % name)

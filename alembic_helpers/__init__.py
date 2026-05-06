# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from alembic.operations import Operations

from .function import DropFunctionOp
from .function import drop_function
from .sequence import CreateSequenceOp
from .sequence import DropSequenceOp
from .sequence import create_sequence
from .sequence import drop_sequence

# Sequence
Operations.register_operation("create_sequence")(CreateSequenceOp)
Operations.implementation_for(CreateSequenceOp)(create_sequence)

Operations.register_operation("drop_sequence")(DropSequenceOp)
Operations.implementation_for(DropSequenceOp)(drop_sequence)

# Function
Operations.register_operation("drop_function")(DropFunctionOp)
Operations.implementation_for(DropFunctionOp)(drop_function)


def register_helpers() -> None:
    pass

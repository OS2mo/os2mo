# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Annotated
from typing import Any
from typing import get_args
from typing import get_origin

from fastapi import Depends
from fastapi.params import Depends as DependsType


def extract_annotated_dependency(T: Annotated[Any, Depends]) -> Any:
    """Extract the dependency injection function from an annotated type.

    This function is useful for extracting the (potentially generated) function
    contained within the annotated type's depends object.

    Example:
        Imagine an annotated type, such as the below exists:

        ```python
        SyncTool = Annotated[_SyncTool, Depends(from_user_context("sync_tool"))]
        ```

        To override this dependency injection in our test-suite, we must set the
        `app.dependency_overrides` on our FastAPI app instance, however to target
        the dependency injection, we must use the return type of `from_user_context`.

        This helper function allows us to extract that from `SyncTool` in the above.

    Args:
        T: The annotated type ready for use in FastAPI dependency injection.

    Returns:
        The function wrapped in the Depends object.
    """
    # Check that 'T' is indeed an annotated type
    assert get_origin(T) is Annotated
    # We expect exactly two arguments to the annotated type
    args = get_args(T)
    assert len(args) == 2
    clazz, depends = args
    # We expect 'clazz' to be a class
    assert issubclass(clazz, clazz)
    # We expect 'depends' to be a FastAPI dependency injection type
    assert isinstance(depends, DependsType)
    # Extract the dependency injection function and return it
    return depends.dependency

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - File."""

from base64 import b64encode
from textwrap import dedent

import strawberry
from strawberry.types import Info

from mora import db
from mora.db import AsyncSession

from ..models import FileStore


@strawberry.type(description="A stored file available for download.")
class File:
    file_store: FileStore = strawberry.field(
        description=dedent(
            """
        The store the file is in.

        The FileStore type lists all possible enum values.
    """
        )
    )

    file_name: str = strawberry.field(
        description=dedent(
            """
        Name of the file.

        Examples:
        * `"report.odt"`
        * `"result.csv"`
        """
        )
    )

    @strawberry.field(
        description=dedent(
            """
        The textual contents of the file.

        Examples:
        * A csv-file:
        ```
        Year,Model,Make
        1997,Ford,E350
        2000,Mercury,Cougar
        ...
        ```
        * A textual report:
        ```
        Status of this Memo

        This document specifies an Internet standards track
        ...
        ```

        Note:
        This should only be used for text files formats such as `.txt` or `.csv`.
        For binary formats please use `base64_contents` instead.
        """
        )
    )
    async def text_contents(self, info: Info) -> str:  # pragma: no cover
        session: AsyncSession = info.context["session"]
        content = await db.files.read(session, self.file_store, self.file_name)
        return content.decode("utf-8")

    @strawberry.field(
        description=dedent(
            """
        The base64 encoded contents of the file.

        Examples:
        * A text file:
        ```
        TW96aWxsYSBQdWJsaWMgTGljZW5zZSBWZXJzaW9uIDIuMAo
        ...
        ```
        * A binary file:
        ```
        f0VMRgIBAQAAAAAAAAAAAAIAPgABAAAAoF5GAAAA
        ...
        ```

        Note:
        While this works for binary and text files alike, it may be preferable to use `text_contents` for text files.
        """
        )
    )
    async def base64_contents(self, info: Info) -> str:
        session: AsyncSession = info.context["session"]
        content = await db.files.read(session, self.file_store, self.file_name)
        return b64encode(content).decode("utf-8")

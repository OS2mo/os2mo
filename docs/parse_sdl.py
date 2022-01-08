#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import json
from pathlib import Path
from typing import Any
from typing import Dict

import graphql as gql
from graphql import utilities as gql_util
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template
from pydantic import BaseSettings

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class Settings(BaseSettings):
    sdl: Path = Path("schema.sdl")
    out: Path = Path("voyager.html")


def main() -> None:
    settings = Settings()

    # Get introspection from loaded schema
    schema: gql.GraphQLSchema = gql_util.build_schema(settings.sdl.read_text())
    introspect: Dict[str, Any] = gql_util.introspection_from_schema(schema)

    # Apply to template & write out
    template: Template = Environment(
        loader=FileSystemLoader(searchpath=".")
    ).get_template("voyager.j2")
    settings.out.write_text(
        template.render(introspection_json=json.dumps({"data": introspect}))
    )


if __name__ == "__main__":
    main()

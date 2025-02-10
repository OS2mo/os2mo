# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from pathlib import Path
from typing import Any

from graphql import GraphQLSchema
from graphql import utilities as gql_util
from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import Template
from pydantic import BaseSettings

try:
    from mora.graphapi.schema import get_schema
    from mora.graphapi.version import LATEST_VERSION
except ImportError:
    raise ImportError(
        "Could not import mora.graphapi. "
        "This script is meant to run in a MO docker image context."
    )

ROOT_PATH = Path(__file__).parent


class Settings(BaseSettings):
    out: Path = ROOT_PATH / "voyager.html"
    search_path: Path = ROOT_PATH


def main() -> None:
    settings = Settings()

    # Get introspection from loaded schema
    schema: GraphQLSchema = gql_util.build_schema(get_schema(LATEST_VERSION).as_str())
    introspect: dict[str, Any] = gql_util.introspection_from_schema(schema)

    # Apply to template & write out
    template: Template = Environment(
        loader=FileSystemLoader(searchpath=settings.search_path)
    ).get_template("voyager.j2")
    settings.out.write_text(
        template.render(introspection_json=json.dumps({"data": introspect}))
    )


if __name__ == "__main__":
    main()

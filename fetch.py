#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from pathlib import Path

import click
import requests
from datamodel_code_generator import generate
from datamodel_code_generator import InputFileType


@click.command()
@click.option(
    "--mox-base",
    default="http://localhost:8080",
    show_default=True,
    help="Address of the MOX host",
)
def gen_models(mox_base: str):
    response = requests.get(mox_base + "/site-map")
    response.raise_for_status()
    site_map = response.json()["site-map"]
    site_map = filter(lambda string: string.endswith("/schema"), site_map)

    for endpoint in site_map:
        resource_name = endpoint.split("/")[-2]
        output_dir = Path(".")
        filename = resource_name + ".py"
        output = Path(output_dir / filename)
        print(filename)

        response = requests.get(mox_base + endpoint)
        response.raise_for_status()
        schema = response.text

        generate(
            schema,
            input_file_type=InputFileType.JsonSchema,
            # input_filename="example.json",
            output=output,
        )


if __name__ == "__main__":
    gen_models()

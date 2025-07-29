# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import base64

import click
import httpx
from more_itertools import one


def _get_token(keycloak_base_url: str, client_id: str, client_secret: str) -> str:
    token_url = f"{keycloak_base_url}/realms/mo/protocol/openid-connect/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    r = httpx.post(token_url, data=payload)
    print(r.status_code, r.url)
    return r.json()["access_token"]


@click.group()
@click.option("--keycloak-base-url", default="http://keycloak:8080/auth")
@click.option("--client-id", default="developer")
@click.option("--client-secret", required=True)
@click.option("--mo-base-url", default="http://localhost:5000")
@click.pass_context
def cli(
    ctx,
    keycloak_base_url: str,
    client_id: str,
    client_secret: str,
    mo_base_url: str,
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["keycloak_base_url"] = keycloak_base_url
    ctx.obj["client_id"] = client_id
    ctx.obj["client_secret"] = client_secret
    ctx.obj["mo_base_url"] = mo_base_url


@cli.command()
@click.option("--mo-file", required=True)
@click.pass_context
def download(
    ctx,
    mo_file: str,
) -> None:
    # Get token from Keycloak
    token = _get_token(
        ctx.obj["keycloak_base_url"],
        ctx.obj["client_id"],
        ctx.obj["client_secret"],
    )

    # Download file from MO

    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "query": "query GetFile($file_name: [String!])"
        "{files(filter: {file_store: EXPORTS, file_names: $file_name})"
        "{objects {file_name base64_contents}}}",
        "variables": {"file_name": mo_file},
        "operationName": "GetFile",
    }
    r = httpx.post(f"{ctx.obj['mo_base_url']}/graphql/v22", headers=headers, json=data)
    print(r.status_code)

    b64_content = one(r.json()["data"]["files"]["objects"])["base64_contents"]
    content = base64.b64decode(b64_content)
    click.echo(content)

@cli.command()
@click.option("--force", is_flag=True)
@click.argument("filename", type=click.Path(exists=True))
@click.pass_context
def upload(
    ctx,
    force: bool,
    filename: click.Path,
) -> None:
    # Get token from Keycloak
    token = _get_token(
        ctx.obj["keycloak_base_url"],
        ctx.obj["client_id"],
        ctx.obj["client_secret"],
    )

    # Upload file to MO

    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "operations": f'{{"query": "mutation($file: Upload!)'
        f"{{upload_file(file_store: EXPORTS, file: $file,"
        f'force: {str(force).lower()})}}","variables":{{"file": null}}}}',
        "map": '{"file": ["variables.file"]}',
    }
    with open(str(filename), "rb") as fp:
        files = {"file": fp}
        r = httpx.post(
            f"{ctx.obj['mo_base_url']}/graphql/v22",
            headers=headers,
            data=data,
            files=files,
        )
        print(r.status_code, r.text)


if __name__ == "__main__":
    cli(obj={})

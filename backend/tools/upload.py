# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import click
import httpx


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
@click.option("--keycloak-base-url", default="http://localhost:8090/auth")
@click.option("--client-id", default="dipex")
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

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import requests

REALM = "mo"
BASEURL = "http://localhost:5000/auth"

# Get token from Keycloak

token_url = BASEURL + f"/realms/{REALM}/protocol/openid-connect/token"
payload = {
    "grant_type": "client_credentials",
    "client_id": "dipex",
    "client_secret": "603f1c82-d012-4d04-9382-dbe659c533fb",
}

r = requests.post(token_url, data=payload)
print(r.status_code, r.url)
token = r.json()["access_token"]

# Call MOs backend with the Keycloak token

headers = {"Authorization": f"bearer {token}"}

r = requests.get("http://localhost:5000/service/o/", headers=headers)
print(r.status_code, r.url)

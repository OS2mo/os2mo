# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import requests

REALM = "lora"
BASEURL = "http://localhost:8081/auth"

# Get token from Keycloak

token_url = BASEURL + f"/realms/{REALM}/protocol/openid-connect/token"
payload = {
    "grant_type": "client_credentials",
    "client_id": "mo",
    "client_secret": "158a2075-aa8a-421c-94a4-2df35377014a",
}

r = requests.post(token_url, data=payload)
print(r.status_code, r.url)
token = r.json()["access_token"]

# Call MOs backend with the Keycloak token

headers = {"Authorization": f"bearer {token}"}

r = requests.get("http://localhost:8080/site-map", headers=headers)
print(r.status_code, r.url)

# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import requests

REALM = "mo"
BASEURL = "http://localhost:5000/auth"

# Get token

token_url = BASEURL + f"/realms/{REALM}/protocol/openid-connect/token"
payload = {
    "client_id": "mo-frontend",
    "username": "bruce",
    "password": "bruce",
    "grant_type": "password",
}

r = requests.post(token_url, data=payload)
token = r.json()["access_token"]

headers = {"Authorization": f"bearer {token}"}

# Call MO

r = requests.get("http://localhost:5000/service/o/", headers=headers)
print(r.status_code, r.url)

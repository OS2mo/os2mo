---
subtitle: Keycloak Authentication
title: Authentication
---

Clients are (per default) required to authenticate when calling LoRas
REST API. Authentication is facilitated by the [OpenID
Connect](https://openid.net/connect/) (OIDC) protocol, and in practice
this means that clients will have to acquire a token from
[Keycloak](https://www.keycloak.org/) and pass this token in the
[Authorization]{.title-ref} header on the requests to LoRa.

This mechanism is exactly the same as the authentication mechanism used
for OS2mo described in [OS2mo authentication
documentation](https://os2mo.readthedocs.io/en/master/operation/auth.html).
Please note that you will have to get a token from Keycloak by using
[client
credentials](https://os2mo.readthedocs.io/en/master/operation/auth.html#by-client-credentials).
In the development environment, Keycloak is configured with the realm
[lora]{.title-ref} and the Keycloak client [mo]{.title-ref} with the
client secret [158a2075-aa8a-421c-94a4-2df35377014a]{.title-ref}

For completeness, a small cURL example is given here (using the
development (environment). First, we need to fetch a token from Keycloak
using the above credentials:

``` {.bash}
$ curl -X POST -d 'grant_type=client_credentials&client_id=mo&client_secret=158a2075-aa8a-421c-94a4-2df35377014a' \
  "http://localhost:8081/auth/realms/lora/protocol/openid-connect/token"
{
  "access_token": "eyJhbGciOiJ...",
  "expires_in": 300,
  "refresh_expires_in": 0,
  "token_type": "Bearer",
  "not-before-policy": 0,
  "scope": "email profile"
}
```

and secondly, we can pass the retrieved [access\_token]{.title-ref} as a
bearer token in the [Authorization]{.title-ref} header when calling a
LoRa endpoint:

``` {.bash}
$ curl -i -H "Authorization: Bearer eyJhbGciOiJ..." "http://localhost:8080/klassifikation/klasse/fields"
{
  "attributter": {
    "egenskaber": [
      "brugervendtnoegle",
      "beskrivelse",
      "eksempel",
      "omfang",
      "titel",
      "retskilde",
      "aendringsnotat",
      "integrationsdata",
      "soegeord"
    ]
  },
  "attributter_metadata": {
    "egenskaber": {
      "brugervendtnoegle": {
        "mandatory": true
      },
      "titel": {
        "mandatory": true
      },
      "soegeord": {
        "type": "soegeord"
      }
    }
  },
  "tilstande": {
    "publiceret": [
      "Publiceret",
      "IkkePubliceret"
    ]
  },
  "relationer_nul_til_en": [
    "ejer",
    "ansvarlig",
    "overordnetklasse",
    "facet"
  ],
  "relationer_nul_til_mange": [
    "redaktoerer",
    "sideordnede",
    "mapninger",
    "tilfoejelser",
    "erstatter",
    "lovligekombinationer"
  ]
}
```

The LoRa authentication mechanism can be disabled by setting the
environment variable [LORA\_AUTH: \"false\"]{.title-ref} on the LoRa
(i.e. [mox]{.title-ref}) container.

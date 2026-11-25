# Deployment

This document gives an overview of what a minimal MO setup needs in production.


## MO

An OCI image is available at [Docker
Hub](https://hub.docker.com/r/magentaaps/os2mo).

Run multiple, otherwise identical, instances of this image. There is no
expectation that MO is only running on a single machine. On a single machine we
recommend running 1 instance pr vCPU.

MO should only be accessible to the reverse proxy.

MO is configured with environment variables.

The only required variables are for keycloak and the database. These are
prefixed with `KEYCLOAK_` and `DB_`, respectively.

```
KEYCLOAK_HOST=...
DB_HOST=...
DB_PASSWORD=...
# and so on...
```

Refer to `mora/config.py` and `oio_rest/config.py` for all options.


## Frontend

An OCI image is available at [Docker
Hub](https://hub.docker.com/r/magentaaps/os2mo-naldo).

The frontend should only be accessible to the reverse proxy.

The frontend is configured with environment variables.

The only required variables are where to locate MO and Keycloak.

```
PUBLIC_BASE_URL: ...
PUBLIC_KEYCLOAK_URL: .../auth
PUBLIC_KEYCLOAK_REALM: "mo"
PUBLIC_KEYCLOAK_CLIENT_ID: "mo-frontend"
```


## Reverse proxy

Run MO behind a reverse proxy.

`/auth` should go to Keycloak.

`/graphql` and `/version` should go to MO.

`/*` (anything else) should go to the frontend.


## Event generator

Same image and configuration as the MO application.

Change the command to `python -m mora.cli amqp start`.

Only run 1.


## Database

MO relies on postgres. Please follow the upstream documentation, or the
recommended way for your platform. As of November 2026, Magenta uses Postgres
18 for MO.


## Keycloak

MO uses Keycloak. Please follow the upstream documentation, or the recommended
way for your platform. While Keycloak might be able to use a database in the
same database server as MO, we do not guarantee that they will be compatible
going forward.

Here are the minimum requirements to work with MO. It is important to still
follow proper Keycloak practices.

* Serve Keycloak under /auth.
* Make a realm (recommended name: `mo`) with `en` locale.
* Make `reader`, `owner` and `admin` roles.
* Make a `mo-frontend` client with:
    * access type `public`,
    * standard flow on,
    * direct access grant on,
    * valid redirect urls at `https://MO_HOST/*`,
    * web origins at `https://MO_HOST` and
    * protocol mapper `uuid-mapper` with type `User Attribute`: user attribute
      from object-guid to token claim uuid. Add it to the ID token, access
      token and userinfo.

Make one client per integration needed. These need:

* access type `confidential`,
* service accounts disabled,
* proper service account roles and
* a protocol mapper `hardcoded-uuid` with type `Hardcoded claim` set to a fixed
  UUID that identifies the actor in MO. For Magenta-developed integrations,
  please use these [well known
  UUIDs](../features/audit-log.md#identifikation-af-integrationer).


## MO init

`init` is a program that initializes MO with a root org, required classes,
facets and the like. It is idempotent so run it as part of the deployment.
Later, it can be used to declaratively create classes and IT systems.

An OCI image is available at [Docker
Hub](https://hub.docker.com/r/magentaaps/os2mo-init).

`init` runs as a separate "integration". Make a client for it in Keycloak.

Configure it with the following environment variables:

* `MO_URL`
* `AUTH_SERVER`
* `AUTH_REALM`
* `CLIENT_ID`
* `CLIENT_SECRET`

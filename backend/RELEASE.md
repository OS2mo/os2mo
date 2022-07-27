Release type: minor

[#50647] Eliminated MO client

LoRa healthchecking now happens via the LoRa client.

Keycloak healthchecking has been removed completely, as we only communicate
with Keycloak once on startup when we fetch the JWKS.

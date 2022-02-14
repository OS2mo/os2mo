Release type: minor

[#48553] Add support for Keycloak Base64 encoded UUID attribute

The ObjectGUID LDAP attribute sent from ADFS to Keycloak, is sent as a Base64
encoded byte-string. There is no easy way to perform conversion of this in
either ADFS or Keycloak, so we add additional support for this eventuality in
our KeycloakToken.

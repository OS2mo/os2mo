#!/bin/bash

echo "Listing"
docker exec -it ldap ldapsearch -x -LLL -h localhost -D "cn=admin,dc=magenta,dc=dk" -w "AdminPassword123" -b "dc=magenta,dc=dk"
echo ""
echo ""

LDIF_FILE=$(mktemp)
echo "dn: uid=abk,ou=os2mo,o=magenta,dc=magenta,dc=dk
changetype: modify
replace: title
title: $1" > "$LDIF_FILE"

echo "Running"
docker cp "$LDIF_FILE" ldap:/modify.ldif
docker exec ldap ldapmodify -x -h localhost -D "cn=admin,dc=magenta,dc=dk" -w "AdminPassword123" -f /modify.ldif
echo ""
echo ""

echo "Listing"
docker exec -it ldap ldapsearch -x -LLL -h localhost -D "cn=admin,dc=magenta,dc=dk" -w "AdminPassword123" -b "dc=magenta,dc=dk"
echo ""
echo ""

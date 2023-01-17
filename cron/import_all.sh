#!/bin/sh

# Get token from /login
# See user_database in main.py
TOKEN=$(
    curl -k -H 'Content-type: application/x-www-form-urlencoded' \
    -d "grant_type=password&username=admin&password=${ADMIN_PASSWORD}" \
    http://mo_ldap_import_export:8000/login \
    | jq '.access_token' \
    | tr -d '"'
)

# Use token to start import
curl -k -H "Authorization: Bearer ${TOKEN}" \
    http://mo_ldap_import_export:8000/Import/all

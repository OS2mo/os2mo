# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""
Local test which connects to Magenta's LDAP as well as to MO on localhost servers.
Before running this make sure MO as well as this app are up-and-running
(docker-compose up)

Created on Mon Oct 24 09:37:25 2022

@author: nick
"""
import random

import requests  # type: ignore

# Get all users from LDAP
r = requests.get("http://0.0.0.0:8000/LDAP/employee")
print("Found a user from LDAP:")
ad_user = r.json()[300]
print(ad_user)
print("")

# Get a user from LDAP (Converted to MO)
r2 = requests.get("http://0.0.0.0:8000/LDAP/employee/%s/converted" % ad_user["cpr"])
print("Here is the same user, MO style:")
print(r2.json())
print("")

# %% Modify a user in LDAP
new_department = (
    "Department which will buy %d cakes for its colleagues" % random.randint(0, 10_000)
)
ldap_person_to_post = {
    "dn": "CN=1212125556,OU=Users,OU=Magenta,DC=ad,DC=addev",
    "name": "Joe Jackson",
    "department": new_department,
    "cpr": "1212125556",
}
requests.post("http://0.0.0.0:8000/LDAP/employee", json=ldap_person_to_post)


# Get the users again - validate that the user is modified
r = requests.get("http://0.0.0.0:8000/LDAP/employee/%s" % ldap_person_to_post["cpr"])
assert r.json()["department"] == new_department
print("Successfully edited department to '%s' in LDAP" % new_department)
print("")


# Get all users from MO
r = requests.get("http://0.0.0.0:8000/MO/employee")
print("Found a user from MO:")
mo_user = r.json()[-12]
print(mo_user)
print("")


# Modify a user in MO (Which should also trigger an LDAP user create/modify)
mo_employee_to_post = mo_user
nickname_givenname = "Man who can do %d push ups" % random.randint(0, 10_000)
mo_employee_to_post["nickname_givenname"] = nickname_givenname
mo_employee_to_post["surname"] = "Hansen_%d" % random.randint(0, 10_000)
mo_employee_to_post["givenname"] = "Hans"

requests.post("http://0.0.0.0:8000/MO/employee", json=mo_employee_to_post)

# Load the user and check if the nickname was changed appropriately
r = requests.get("http://0.0.0.0:8000/MO/employee/%s" % mo_employee_to_post["uuid"])
assert r.json()["surname"] == mo_employee_to_post["surname"]
assert r.json()["nickname_givenname"] == nickname_givenname
print("Successfully edited nickname_givenname to '%s' in MO" % nickname_givenname)

# Check that the user is now also in LDAP, and that his name is correct
r = requests.get("http://0.0.0.0:8000/LDAP/employee/%s" % mo_employee_to_post["cpr_no"])
assert r.json()["givenName"] == mo_employee_to_post["givenname"]
assert r.json()["sn"] == mo_employee_to_post["surname"]

# Print the hyperlink to the employee.
print("")
url = "http://localhost:5000/medarbejder/%s#medarbejder" % mo_employee_to_post["uuid"]
print("see:\n%s\nto validate that the nickname/name was appropriately changed" % url)

# Finish
print("Success")

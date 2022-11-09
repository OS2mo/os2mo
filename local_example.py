# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
#
# SPDX-License-Identifier: MPL-2.0
"""
Local test which connects to Magenta's AD as well as to MO on localhost servers. Before
running this make sure MO as well as this app are up-and-running (docker-compose up)

Created on Mon Oct 24 09:37:25 2022

@author: nick
"""
import random
from uuid import uuid4

import requests  # type: ignore

# Get all users from AD
r = requests.get("http://0.0.0.0:8000/AD/employee")
print("Found a user from AD:")
print(r.json()[-2])
print("")


# Modify a user in AD
ldap_person_to_post = r.json()[-2]
new_department = (
    "Department which will buy %d cakes for its colleagues" % random.randint(0, 10_000)
)
ldap_person_to_post = {
    "dn": "CN=Lars Peter Thomsen,OU=Users,OU=Magenta,DC=ad,DC=addev",
    "Name": "Lars Peter Thomsen",
    "Department": new_department,
}
requests.post("http://0.0.0.0:8000/AD/employee", json=ldap_person_to_post)


# Get the users again - validate that the user is modified
r = requests.get("http://0.0.0.0:8000/AD/employee/%s" % ldap_person_to_post["dn"])
assert r.json()["Department"] == new_department
print("Successfully edited department to '%s' in AD" % new_department)
print("")


# Get all users from MO
r = requests.get("http://0.0.0.0:8000/MO/employee")
print("Found a user from MO:")
print(r.json()[-1])
print("")


# Post a new user to MO (Which should also trigger an AD user create)
nickname_givenname = "Man who can do %d push ups" % random.randint(0, 10_000)
mo_employee_to_post = {}
mo_employee_to_post["uuid"] = str(uuid4())
mo_employee_to_post["nickname_givenname"] = nickname_givenname
mo_employee_to_post["surname"] = "Hansen" + " %d" % random.randint(0, 10_000)
mo_employee_to_post["givenname"] = "Hans"
requests.post("http://0.0.0.0:8000/MO/employee", json=mo_employee_to_post)

# Load the user and check if the nickname was changed appropriately
r = requests.get("http://0.0.0.0:8000/MO/employee/%s" % mo_employee_to_post["uuid"])
assert r.json()["nickname_givenname"] == nickname_givenname
print("Successfully edited nickname_givenname to '%s' in MO" % nickname_givenname)

# Check that the user is now also in AD, and that his name is correct
dn = "CN=%s %s,OU=Users,OU=Magenta,DC=ad,DC=addev" % (
    mo_employee_to_post["givenname"],
    mo_employee_to_post["surname"],
)
r = requests.get("http://0.0.0.0:8000/AD/employee/%s" % dn)
assert r.json()["Name"] == "%s %s" % (
    mo_employee_to_post["givenname"],
    mo_employee_to_post["surname"],
)

# Modify the user in MO

# Check that it is also modified in AD

# Print the hyperlink to the employee.
print("")
url = "http://localhost:5000/medarbejder/%s#medarbejder" % mo_employee_to_post["uuid"]
print("see:\n%s\nto validate that the nickname/name was appropriately changed" % url)

# Finish
print("Success")

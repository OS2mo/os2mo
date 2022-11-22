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
import json
import random

import pandas as pd
import requests  # type: ignore

# Dataframe display settings
pd.set_option("display.large_repr", "info")
pd.set_option("display.max_info_columns", 1000)


def reduce_dict(d):
    # Returns a dict with only the relevant parameters for nested entries
    return {
        "cpr": d["cpr"],
        "dn": d["dn"],
    }


# Cleans out None values and nested dicts so we can print it on screen.
def clean_dict(d):
    output_dict = {}
    for key, value in d.items():
        if value is None:
            # Remove empty values
            continue
        elif type(value) is dict:
            # Cleanup nested entries
            if "cpr" in value.keys():
                output_dict[key] = reduce_dict(value)
            else:
                output_dict[key] = value
        elif type(value) is list:
            cleaned_list = []
            for list_entry in value:
                if type(list_entry) is dict:
                    if "cpr" in list_entry.keys():
                        list_entry = reduce_dict(list_entry)
                cleaned_list.append(list_entry)
            output_dict[key] = cleaned_list
        else:
            output_dict[key] = value

    return output_dict


def pretty_print(d):
    print(json.dumps(clean_dict(d), sort_keys=True, indent=4))


# %% Get all users from LDAP
r = requests.get("http://0.0.0.0:8000/LDAP/employee")
print("Found all user from LDAP:")
df = pd.DataFrame(r.json())
print(df)
print("")

# Get a single user from LDAP
ad_user = r.json()[300]
cpr = ad_user["employeeID"]
r2 = requests.get(f"http://0.0.0.0:8000/LDAP/employee/{cpr}")
print("Here is a single user:")
ad_user_detailed = r2.json()
pretty_print(ad_user_detailed)

# Get his manager from LDAP
manager_cpr = ad_user_detailed["manager"]["employeeID"]
r3 = requests.get(f"http://0.0.0.0:8000/LDAP/employee/{manager_cpr}")
print("Here is his manager:")
pretty_print(r3.json())

# Get a user from LDAP (Converted to MO)
r4 = requests.get(f"http://0.0.0.0:8000/LDAP/employee/{cpr}/converted")
print("Here is the same user, MO style:")
pretty_print(r4.json())
print("")

# %% Modify a user in LDAP
random_int = random.randint(0, 10_000)
new_department = f"Department which will buy {random_int} cakes for its colleagues"

ldap_person_to_post = {
    "dn": "CN=1212125557,OU=Users,OU=Magenta,DC=ad,DC=addev",
    "name": "Joe Jackson",
    "department": new_department,
    "employeeID": "1212125556",
}
requests.post("http://0.0.0.0:8000/LDAP/employee", json=ldap_person_to_post)


# Get the users again - validate that the user is modified
cpr = ldap_person_to_post["employeeID"]
r = requests.get(f"http://0.0.0.0:8000/LDAP/employee/{cpr}")
assert r.json()["department"] == new_department
print(f"Successfully edited department to '{new_department}' in LDAP")
print("")


# Get all users from MO
r = requests.get("http://0.0.0.0:8000/MO/employee")
print("Found a user from MO:")
mo_user = r.json()[-12]
print(mo_user)
print("")


# Modify a user in MO (Which should also trigger an LDAP user create/modify)
mo_employee_to_post = mo_user
random_int = random.randint(0, 10_000)
nickname_givenname = f"Man who can do {random_int} push ups"
mo_employee_to_post["nickname_givenname"] = nickname_givenname
random_int = random.randint(0, 10_000)
mo_employee_to_post["surname"] = f"Hansen_{random_int}"
mo_employee_to_post["givenname"] = "Hans"

requests.post("http://0.0.0.0:8000/MO/employee", json=mo_employee_to_post)

# Load the user and check if the nickname was changed appropriately
uuid = mo_employee_to_post["uuid"]
r = requests.get(f"http://0.0.0.0:8000/MO/employee/{uuid}")
assert r.json()["surname"] == mo_employee_to_post["surname"]
assert r.json()["nickname_givenname"] == nickname_givenname
print(f"Successfully edited nickname_givenname to '{nickname_givenname}' in MO")

# Check that the user is now also in LDAP, and that his name is correct
cpr = mo_employee_to_post["cpr_no"]
r = requests.get(f"http://0.0.0.0:8000/LDAP/employee/{cpr}")
assert r.json()["givenName"] == mo_employee_to_post["givenname"]
assert r.json()["sn"] == mo_employee_to_post["surname"]
print("Validated that the changes are reflected in LDAP")

# Print the hyperlink to the employee.
print("")
uuid = mo_employee_to_post["uuid"]
url = "http://localhost:5000/medarbejder/{uuid}#medarbejder"
print(f"see:\n{url}\nto validate that the nickname/name was appropriately changed")

# %% get an overview of all information in LDAP
r = requests.get("http://0.0.0.0:8000/LDAP/overview")
overview = r.json()
print("Here is an overview of the classes in the LDAP structure:")
print("[")
for p in list(overview.keys())[:10]:
    print(p)
print("...]")

print("")

print("Here are the attributes which belong to user:")
print("[")
for p in list(overview["user"]["attributes"])[:10]:
    print(p)
print("...]")

# %% And an overview which only contains fields that actually contain data:
r = requests.get("http://0.0.0.0:8000/LDAP/overview/populated")
populated_overview = r.json()

print("And here are the fields that actually contain data for a user:")
pretty_print(populated_overview["user"])

print("Here are all the fields that actually contain data:")
pretty_print(populated_overview)


# %% Get all converted users from LDAP
r = requests.get("http://0.0.0.0:8000/LDAP/employee/converted")
print("Converted all user from LDAP:")
df = pd.DataFrame(r.json())
print(df)
print("")

# %% Finish
print("Success")

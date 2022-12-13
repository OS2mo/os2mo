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
import time

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


def pretty_print(list_or_dict):
    if type(list_or_dict) is not list:
        list_or_dict = [list_or_dict]

    for d in list_or_dict:
        print(json.dumps(clean_dict(d), sort_keys=True, indent=4))


# %% Get all users from LDAP
r = requests.get("http://0.0.0.0:8000/LDAP/Employee")
print("Found all users from LDAP:")
df = pd.DataFrame(r.json())
print(df)
print("")

r = requests.get("http://0.0.0.0:8000/LDAP/Lokation")
print("Found all post addresses from LDAP:")
df = pd.DataFrame(r.json())
print(df)
print("")

# Get a single user from LDAP
ad_user = r.json()[300]
cpr = ad_user["employeeID"]
r2 = requests.get(f"http://0.0.0.0:8000/LDAP/Employee/{cpr}")
print("Here is a single user:")
ad_user_detailed = r2.json()
pretty_print(ad_user_detailed)

# Get his manager from LDAP
# manager_cpr = ad_user_detailed["manager"]["employeeID"]
# r3 = requests.get(f"http://0.0.0.0:8000/LDAP/Employee/{manager_cpr}")
# print("Here is his manager:")
# pretty_print(r3.json())

# Get his mail address
r4 = requests.get(f"http://0.0.0.0:8000/LDAP/Email/{cpr}")
print("Here is his mail address:")
ad_user_detailed = r4.json()
pretty_print(ad_user_detailed)

# Get his post address(es)
r4 = requests.get(f"http://0.0.0.0:8000/LDAP/Lokation/{cpr}")
print("Here is his post address:")
ad_user_detailed = r4.json()
pretty_print(ad_user_detailed)

# Get a user from LDAP (Converted to MO)
for json_key in ["Employee", "Email", "Lokation"]:
    cpr = ad_user["employeeID"]
    r5 = requests.get(f"http://0.0.0.0:8000/LDAP/{json_key}/{cpr}/converted")
    if r5.status_code == 202:
        print(f"Here is the {json_key}, MO style:")
        pretty_print(r5.json())
        print("")
    else:
        print(f"Could not obtain {json_key}, MO style.")

# %% Modify a user in LDAP
random_int = random.randint(0, 10_000)
new_department = f"Department which will buy {random_int} cakes for its colleagues"

ldap_person_to_post = {
    "dn": "CN=1212125557,OU=Users,OU=Magenta,DC=ad,DC=addev",
    "name": "Joe Jackson",
    "department": new_department,
    "employeeID": "1212125556",
}
requests.post("http://0.0.0.0:8000/LDAP/Employee", json=ldap_person_to_post)


# Get the users again - validate that the user is modified
cpr = ldap_person_to_post["employeeID"]
r = requests.get(f"http://0.0.0.0:8000/LDAP/Employee/{cpr}")
assert r.json()["department"] == new_department
print(f"Successfully edited department to '{new_department}' in LDAP")
print("")


# Get a user from MO
uuid = "9af20c47-0d81-410e-8789-f28dadc5cee3"
r = requests.get(f"http://0.0.0.0:8000/MO/Employee/{uuid}")
print("Found a user from MO:")
mo_user = r.json()
pretty_print(mo_user)
print("")


# Modify this user in MO (Which should also trigger an LDAP user create/modify)
mo_employee_to_post = mo_user
random_int = random.randint(0, 10_000)
nickname_givenname = f"Man who can do {random_int} push ups"
mo_employee_to_post["nickname_givenname"] = nickname_givenname
random_int = random.randint(0, 10_000)
mo_employee_to_post["surname"] = f"Hansen_{random_int}"
mo_employee_to_post["givenname"] = "Hans"

requests.post("http://0.0.0.0:8000/MO/Employee", json=mo_employee_to_post)

# Load the user and check if the nickname was changed appropriately
uuid = mo_employee_to_post["uuid"]
r = requests.get(f"http://0.0.0.0:8000/MO/Employee/{uuid}")
assert r.json()["surname"] == mo_employee_to_post["surname"]
assert r.json()["nickname_givenname"] == nickname_givenname
print(f"Successfully edited nickname_givenname to '{nickname_givenname}' in MO")

# Check that the user is now also in LDAP, and that his name is correct
cpr = mo_employee_to_post["cpr_no"]
r = requests.get(f"http://0.0.0.0:8000/LDAP/Employee/{cpr}")
assert r.json()["givenName"] == mo_employee_to_post["givenname"]
assert r.json()["sn"] == mo_employee_to_post["surname"]
print("Validated that the changes are reflected in LDAP")

# Print the hyperlink to the employee.
print("")
uuid = mo_employee_to_post["uuid"]
url = "http://localhost:5000/medarbejder/{uuid}#medarbejder"
print(f"see:\n{url}\nto validate that the nickname/name was appropriately changed")

# %% get an overview of all information in LDAP
r = requests.get("http://0.0.0.0:8000/LDAP_overview")
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

print("Here is the attribute type info for the 'postalAddress' field:")
print(overview["user"]["attribute_types"]["postalAddress"])

print("")
print("Here are the 'user' attributes which can contain multiple values:")

single_value_dict = {
    key: overview["user"]["attribute_types"][key]["single_value"]
    for key in overview["user"]["attribute_types"].keys()
}

multi_value_attributes = []
for key, value in single_value_dict.items():
    if not value:
        multi_value_attributes.append(key)

print("[")
for p in sorted(multi_value_attributes):
    print(p)
print("]")


# %% And an overview which only contains fields that actually contain data:
r = requests.get("http://0.0.0.0:8000/LDAP_overview/populated")
populated_overview = r.json()

print("And here are the fields that actually contain data for a user:")
pretty_print(populated_overview["user"])

print("Here are all the fields that actually contain data:")
pretty_print(populated_overview)

number_of_user_attributes = len(overview["user"]["attributes"])
number_of_populated_user_attributes = len(populated_overview["user"]["attributes"])
assert number_of_user_attributes != number_of_populated_user_attributes

# %% Get all converted users from LDAP
for json_key in ["Employee", "Email", "Lokation"]:
    r = requests.get(f"http://0.0.0.0:8000/LDAP/{json_key}/converted")
    print(f"Converted all {json_key}s from LDAP:")
    df = pd.DataFrame(r.json())
    print(df)
    print("")

# %% Modify an email address in MO and check if it was also modified in AD
# Note: mail address gets overwritten because the email field which we specify can only
# contain one value
# Request an email address
uuid = "00513f7c-5aed-466a-966d-35537025d72d"
r = requests.get(f"http://0.0.0.0:8000/MO/Address/{uuid}")

print("Here is an address:")
pretty_print(r.json()[0])
address_to_post = r.json()[0]
meta_data = r.json()[1]

person_uuid = address_to_post["person"]["uuid"]
url = f"http://localhost:5000/medarbejder/{person_uuid}#medarbejder"

print(f"It belongs to {url}")

random_int = random.randint(0, 10_000)
address_to_post["value"] = f"foo_{random_int}@hotmail.com"

# Modify this address
r = requests.post("http://0.0.0.0:8000/MO/Email", json=address_to_post)

# Check that it is also modified in LDAP
cpr = meta_data["employee_cpr_no"]

n = 0
while True:
    person_from_ldap = requests.get(f"http://0.0.0.0:8000/LDAP/Email/{cpr}").json()
    try:
        assert person_from_ldap["mail"] == address_to_post["value"]
        print("mail address succesfully modified in LDAP")
        break
    except AssertionError:
        time.sleep(1)

        if n < 5:
            n += 1
            continue
        else:
            break
            print("mail address was not modified in LDAP")

# %% Finish
print("Success")

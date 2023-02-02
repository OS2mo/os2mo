### Running the tests

You use `poetry` and `pytest` to run the tests:

`poetry run pytest -s`

You can also run specific files

`poetry run pytest tests/<test_folder>/<test_file.py>`

and even use filtering with `-k`

`poetry run pytest -k "Manager"`

You can use the flags `-vx` where `v` prints the test & `x` makes the test stop if any tests fails (Verbose, X-fail)

You can get the coverage report like this:

`poetry run pytest -s --cov --cov-report term-missing -vvx`

### Using the app

First make sure that os2mo is up and running.

Then, create a `docker-compose.override.yml` file based on the
`docker-compose.override.template.yml` file

You can then boot the app like this:

```
poetry lock
poetry install
docker-compose up
```

You can use the app like this:

```
import requests
r = requests.get("http://0.0.0.0:8000/LDAP/all")
print(r.json()[-2])
```

Or you can go to [the swagger documentation][swagger] for a more
graphic interface

### Setting up conversion file

The conversion dictionary is the heart of the application. New fields can be synchronized
solely by adding entries to this dictionary, without the need to change code elsewhere.

Currently only MO addresses and employees are supported for conversion. All address types
are supported.

#### Employee conversion

The conversion file specifies in json how to map attributes from MO to LDAP and from LDAP
to MO, and takes the form:

```
{
  "ldap_to_mo":
    "Employee": {
      "objectClass": "ramodels.mo.employee.Employee",
      [other attributes]
    },
    [other classes]
  },
  "mo_to_ldap":
    "Employee": {
      "objectClass": "user",
      [other attributes]
    },
    [other classes]
  }
}
    
```
Note that the `Employee` key must always be present in the conversion file.

Here the `Employee` class is specified to take the class `ramodels.mo.employee.Employee`
when creating or updating a MO object, and to take the class `user` when creating or
updating an LDAP object. If the LDAP schema uses a different class for the employee
object, specify that class here.



Each entry in the conversion file _must_ specify:
* An "objectClass" attribute.
    * MO: Any MO class from ramodels should be acceptable.
    * LDAP: Available LDAP classes and their attributes can be retrieved by calling
    [GET:LDAP_overview][get_overview].
* An attribute that corresponds to the cpr number for the MO or LDAP class.
* Attributes for all required fields in the MO or LDAP class to be written
* For LDAP classes: a link to mo_employee.cpr_no must be present.
Otherwise we do not know who the address belongs to.


Note that all attributes MUST be accepted by the destination class in MO or LDAP.

Values in the json structure may be normal strings, or a string containing one or more
jinja2 templates, to be used for extracting values. For example:

```
  [...]
  "mo_to_ldap": {
    "Employee": {
      "objectClass": "user",
      "employeeID": "{{mo_employee.cpr_no}}",
    }
  }
  [...]
```
Here, `employeeID` in the resulting LDAP object will be set to the `cpr_no` value from
the MO object. The `mo_employee` object will be added to the template context by adding
to the `mo_object_dict` in `mo_import_export.main.listen_to_changes_in_employees`.

More advanced template strings may be constructed, such as:
```
  [...]
  "ldap_to_mo": {
    "Employee": {
      "objectClass": "user",
      "givenname": "{{ldap.givenName or ldap.name|splitlast|first}}",
    }
  }
  [...]
```
Here, the MO object's `givenname` attribute will be set to the givenName attribute from
LDAP, if it exists, or if it does not, to the name attribute modified to be split by the
last space and using the first part of the result.

#### Address conversion

MO can contain multiple addresses of the same type for a single user. It is therefore
recommended that the LDAP field corresponding to MO's address value can contain multiple
values. If this is not the case, the address in LDAP will be overwritten every time a
new address of an existing type is added in MO. Information about whether an LDAP field
can contain multiple values can be found by calling [GET:LDAP_overview][get_overview].
and inspecting the `single_value` attribute
in `["{class_name}"]["attribute_types"]["{attribute_name}"]`. For example:

```
r = requests.get("http://0.0.0.0:8000/LDAP_overview")
overview = r.json()
print("Here is the attribute type info for the 'postalAddress' field:")
print(overview["user"]["attribute_types"]["postalAddress"])
```

Returns:

```
>>> {'oid': '2.5.4.16',
     'name': ['postalAddress'],
     'description': None,
     'obsolete': False,
     'extensions': None,
     'experimental': None,
     'raw_definition': "( 2.5.4.16 NAME 'postalAddress' SYNTAX '1.3.6.1.4.1.1466.115.121.1.15' )",
     '_oid_info': None,
     'superior': None,
     'equality': None,
     'ordering': None,
     'substring': None,
     'syntax': '1.3.6.1.4.1.1466.115.121.1.15',
     'min_length': None,
     'single_value': False,
     'collective': False,
     'no_user_modification': False,
     'usage': None,
     'mandatory_in': [],
     'optional_in': ['organizationalUnit',
      'organizationalPerson',
      'organization',
      'residentialPerson',
      'rFC822LocalPart',
      'organizationalRole']}
```

An example of an address conversion dict is as follows:

```
  [...]
  "mo_to_ldap": {
    "Email": {
      "objectClass": "user",
      "mail": "{{mo_address.value}}",
      "employeeID": "{{mo_employee.cpr_no}}"
    }
  }
  [...]
```

Note the presence of the `mo_employee.cpr_no` field. This field must be present, for the
application to know who this address belongs to. Furthermore, the `Email` key must be a
valid MO address type name. MO address types can be retrieved by calling
[GET:MO/Address_types][get_address_types]. Finally it is recommended that LDAP's `mail`
attribute is a multi-value field.

Converting the other way around can be done as follows:

```
  [...]
  "ldap_to_mo": {
    "Email": {
      "objectClass": "ramodels.mo.details.address.Address",
      "value": "{{ldap.mail or None}}",
      "type": "address",
      "validity": "{{ dict(from_date = ldap.mail_validity_from or now()|mo_datestring) }}",
      "address_type": "{{ dict(uuid=get_address_type_uuid('Lokation')) }}"
    },
  }
  [...]
```

Note the uuid in the `address_type` field. This value must be a dict, as specified by
`ramodels.mo.details.address.Address`. Furthermore the uuid must be a valid address type
uuid. Valid address type uuids can be obtained by calling
[GET:MO/Address_types][get_address_types] or by using the `get_address_type_uuid` global
function in the template.


##### Post Address conversion

For post addresses, it is required to use an address type in MO with `scope` != `DAR`.
The reason for this is that we cannot expect an LDAP server to have the same address
format as DAR.

##### Organization unit address conversion

An address in an OS2mo organizational unit maps to every LDAP employee object who is
engaged at the organizational unit. This can be set up as follows:

```
  [...]
  "mo_to_ldap": {
    "LocationUnit": {
      "objectClass": "user",
      "postalAddress": "{{mo_org_unit_address.value}}",
      "employeeID": "{{mo_employee.cpr_no}}",
      "division": "{{get_org_unit_path_string(mo_org_unit_address.org_unit.uuid)}}"
    }
  }
  [...]
```

And the other way around:

```
  [...]
  "ldap_to_mo": {
    "LocationUnit": {
      "objectClass": "ramodels.mo.details.address.Address",
      "value": "{{ ldap.postalAddress or NONE }}",
      "type": "address",
      "validity": "{{ dict(from_date=now()|mo_datestring) }}",
      "address_type": "{{ dict(uuid=get_address_type_uuid('LocationUnit')) }}",
      "org_unit": "{{ dict(uuid=get_or_create_org_unit_uuid(ldap.division)) }}"
    },
  }
  [...]
```

Note that an organizational unit address needs to have an `org_unit` attribute. In
contrast to an employee address, which needs a `person` attribute. For details regarding
`get_org_unit_path_string` and `get_or_create_org_unit_uuid`, see the chapter on
[engagement conversion](#engagement-conversion).

Mapping org unit addresses to LDAP objects other than `employee` objects (i.e. objects
with a cpr number field) is currently not supported.

#### IT user conversion
It user conversion follows the same logic as address conversion. An example of an IT
user conversion dict is as follows:

```
  [...]
  "mo_to_ldap": {
    "Active Directory": {
      "objectClass": "user",
      "msSFU30Name" : "{{mo_it_user.user_key}}",
      "employeeID": "{{mo_employee.cpr_no}}"
    }
  }
  [...]
```

And the other way around:

```
  [...]
  "ldap_to_mo": {
    "Active Directory": {
      "objectClass": "ramodels.mo.details.it_system.ITUser",
      "user_key": "{{ ldap.msSFU30Name or None }}",
      "itsystem": "{{ dict(uuid=get_it_system_uuid('Active Directory')) }}",
      "validity": "{{ dict(from_date=now()|mo_datestring) }}"
            }
  }
  [...]
```

Note that we have specified the json key equal to `Active Directory`. This key needs
to be an IT system name in MO. IT system names can be retrieved using
[GET:MO/IT_systems][get_it_systems].

#### Engagement conversion
Engagement conversion follows the same logic as address conversion. An example of
an engagement conversion dict is as follows:

```
  [...]
  "mo_to_ldap": {
    "Engagement" : {
      "objectClass": "user",
      "employeeID": "{{mo_employee.cpr_no}}",
      "department": "{{NONE}}",
      "company": "{{NONE}}",
      "departmentNumber": "{{mo_engagement.user_key}}",
      "division": "{{get_org_unit_path_string(mo_engagement.org_unit.uuid)}}",
      "primaryGroupID": "{{NONE}}",
      "employeeType": "{{get_engagement_type_name(mo_engagement.engagement_type.uuid)}}",
      "memberOf": "{{NONE}}",
      "personalTitle": "{{NONE}}",
      "title": "{{get_job_function_name(mo_engagement.job_function.uuid)}}"
    }
  }
  [...]
```

Note the `get_org_unit_path_string` function which we use for ldap.division. This will
write full organizational paths to ldap, rather than just the name of an organizational
unit. Converting the other way around can be done like this:

```
  [...]
  "ldap_to_mo": {
    "Engagement": {
      "objectClass": "ramodels.mo.details.engagement.Engagement",
      "org_unit": "{{ dict(uuid=get_or_create_org_unit_uuid(ldap.division)) }}",
      "job_function": "{{ dict(uuid=get_job_function_uuid(ldap.title)) }}",
      "engagement_type": "{{ dict(uuid=get_engagement_type_uuid(ldap.employeeType)) }}",
      "user_key": "{{ ldap.departmentNumber or uuid4() }}",
      "validity": "{{ dict(from_date=now()|mo_datestring) }}"
    }
  }
  [...]
```

Note that `get_or_create_org_unit_uuid` supports full organization paths as input. This
means, that if the `ldap.division` field contains a string which reads
`Magenta Aps->Magenta Aarhus`, it will try to get the uuid of the organizational unit
called `Magenta Aarhus`. In case there are multiple organizational units with this name,
it will find the right one. If this unit does not exist, it will create it, with
`Magenta Aps` as its parent. It is important that `ldap.division` contains full paths
to its organizational unit. This is important because organizational units can
have duplicate names. For example: Every sub-organizational unit in most companies has
an `IT Support` department.

Created organizational units are called `IMPORTED FROM LDAP: {name}`. They have a
default organizational unit type and level specified in the environment variables with
`DEFAULT_ORG_UNIT_TYPE` and `DEFAULT_ORG_UNIT_LEVEL`. The idea is that users manually go
in and remove the `IMPORTED FROM LDAP` tag. While they are doing this they can also set
the proper level and type for the organization.

#### Filters and globals

In addition to the [Jinja2's builtin filters][jinja2_filters],
the following filters are available:

* `splitfirst`: Splits a string at the first space, returning two elements
  This is convenient for splitting a name into a givenName and a surname
  and works for names with no spaces (surname will then be empty).
* `splitlast`: Splits a string at the last space, returning two elements
  This is convenient for splitting a name into a givenName and a surname
  and works for names with no spaces (givenname will then be empty).
* `mo_datestring`: Accepts a datetime object and formats it as a string.
* `strip_non_digits`: Removes all but digits from a string.
* `parse_datetime`: Converts a date string to a datetime object. The year needs to be
  first. For example `2021-01-01`.

In addition to filters, a few methods have been made available for the templates.
These are called using the normal function call syntax:
```
{
  "key": "{{ nonejoin(ldap.postalCode, ldap.streetAddress) }}"
}
```
* `now`: Returns current datetime
* `nonejoin`: Joins two or more strings together with comma, omitting any Falsy values
  (`None`, `""`, `0`, `False`, `{}` or `[]`)
* `get_address_type_uuid`: Returns the address type uuid for an address type string
* `get_it_system_uuid`: Returns the it system uuid for an it system string
* `get_or_create_org_unit_uuid`: Returns the organization unit uuid for an organization
  unit path string. Note that the input string needs to be the full path to the
  organization unit, separated by `->`. If this organization unit does not exist, it
  is created.
* `get_job_function_uuid`: Returns the job function uuid for a job function string
* `get_engagement_type_uuid`: Returns the engagement type uuid for an engagement type
  string
* `uuid4`: Returns an uuid4
* `get_org_unit_path_string`: Returns the full path string to an organization unit,
  given its uuid
* `get_engagement_type_name`: Returns the name of an engagement type, given its uuid
* `get_job_function_name`: Returns the name of a job function, given its uuid

Finally, the following global variables can be used:

* `employee_uuid`: uuid of the employee matching the converted object's cpr number.

#### Username generation
If a user is created in MO, the tool will try to find the matching user in LDAP using
a CPR-number lookup. If the user does not exist in LDAP a username is generated and
the user is created in LDAP. Username generation follows patterns set in the json file.
For example:

```
  [...]
  "username_generator": {
    "objectClass" : "UserNameGenerator",
    "combinations_to_try": ["F123L",
                            "F12LL",
                            "F1LLL",
                            "FLLLL",
                            "FLLLLX"],
    "char_replacement": {"ø": "oe",
                         "æ": "ae",
                         "å": "aa",
                         "Ø": "oe",
                         "Æ": "ae",
                         "Å": "aa"
                         },
    "forbidden_usernames": ["hater",
                            "lazer"]
  }
  [...]
```

The examples which follow use this json file.

`objectClass` points to an object class in `usernames.py` which should be used for
username generation. Currently only `UserNameGenerator` is accepted. If desired, new
classes can be added to `usernames.py` and specified in the json file. The only
requirement of a username generator class is that it has a function called
`generate_dn`, which returns a string.

`combinations_to_try` provides patterns to use for generating usernames. Patterns are
tried starting with the first one, going down. If the first pattern is not a possible
pattern for some reason, the next one is attempted. The following characters are
accepted:

* `F`: First name
* `1`: First middle name
* `2`: Second middle name
* `3`: Third middle name
* `L`: Last name
* `X`: A number to add to the username

When using a json file such as the one printed above, a person named `Jens Hansen`
will get `jhans` as a username. The username flow is as follows:

* `F123L` does not match because the person has no middle names
* `F12LL` does not match because the person has no middle names
* `F1LLL` does not match because the person has no middle names
* `FLLLL` matches. The username becomes `jhans`

if `jhans` already exists, the username will be `jhans2`:

* `F123L` does not match because the person has no middle names
* `F12LL` does not match because the person has no middle names
* `F1LLL` does not match because the person has no middle names
* `FLLLL` does not match. The username `jhans` already exists
* `FLLLLX` matches. The username becomes `jhans2`

Similarly, a person named `Jens Hans Hansen` will get `jhhan` as a username:

* `F123L` does not match because the person has no second/third middle name
* `F12LL` does not match because the person has no second middle name
* `F1LLL` matches. The username becomes `jhhan`

`char_replacement` must be a dictionary with characters to replace when creating a
username. For example: A person named `Jens Åberg` will get username `jaabe`, instead of
`jåber`:

* `Jens Åberg` becomes `Jens aaberg` after character replacement
* `F123L` does not match because the person has no middle names
* `F12LL` does not match because the person has no middle names
* `F1LLL` does not match because the person has no middle names
* `FLLLL` matches. The username becomes `jaabe`

`forbidden_usernames` is a list of usernames which are not allowed. For example: A
person named `Hans Åberg Terp` will get username `hterp`:

* `Hans Åberg Terp` becomes `Hans aaberg Terp` after character replacement
* `F123L` does not match because the person has no second/third middle name
* `F12LL` does not match because the person has no second middle name
* `F1LLL` matches, but returns username `hater`, which is forbidden.
* `FLLLL` also matches. The username becomes `hterp`

If none of the patterns match, a runtime error is returned. Note also, that a pattern
such as `FLLLL` will fail, if a person has a last name which has less than four
characters. To avoid errors, it is therefore recommended to:

* Have at least a couple of patterns which contain an `X`
* Have some short patterns in the list as well. Even though it might be required to have
  (for example) a 5-character username, there should still be some 2 or 3-character
  patterns in the list for people who have particularly short first or last names.

If these patterns are highly undesirable, put them in the bottom of the list, and they
will only be used if everything else fails.


[swagger]:http://localhost:8000/docs
[get_overview]:http://localhost:8000/docs#/LDAP/load_overview_from_LDAP_LDAP_overview_get
[get_address_types]:http://localhost:8000/docs#/MO/load_address_types_from_MO_MO_Address_types_get
[get_it_systems]:http://localhost:8000/docs#/MO/load_it_systems_from_MO_MO_IT_systems_get
[jinja2_filters]:https://jinja.palletsprojects.com/en/3.1.x/templates/#builtin-filters

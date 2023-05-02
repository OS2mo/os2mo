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

First make sure that OS2mo is up and running.

Then, create a `docker-compose.override.yml` file based on the
`docker-compose.override.template.yml` file

You can then boot the app like this:

```
poetry lock
poetry install
docker-compose up
```

To interact with the app, you can go to [the swagger documentation][swagger].

#### Importing from LDAP to OS2mo
Objects can be imported from LDAP to OS2mo in two ways:
* A single user can be imported using [GET:/Import/dn][get_import_single]
* All users can be imported using [GET:/Import/all][get_import_all]

#### Exporting from OS2mo to LDAP
Objects can be exported from OS2mo to LDAP by using [POST:/Export][post_export_all].
Note that only objects which are properly defined in the conversion file are exported.

#### Synchronization between OS2mo and LDAP
OS2mo and LDAP are kept ajour by two seperate processes:
* An LDAP listener runs in the background and listens to any changes in LDAP. The
  listener will respond within 5 seconds by calling `sync_tool.import_single_user(dn)`
  on a changed ldap object, when any of its attributes are modified in LDAP.
  Note that this can also cause non-employee objects to be imported, if those are in
  the LDAP search base.
* An AMQP listener runs in the background and listens to AMQP messages sent out by
  OS2mo. As soon as the listener receives an AMQP message, the matching OS2mo object is
  exported to LDAP.


### Setting up the conversion file

The conversion dictionary is the heart of the application. New fields can be synchronized
solely by adding entries to this dictionary, without the need to change code elsewhere.

Currently the following objects are supported for conversion:

* Employees
* Employee addresses
* Employee IT users
* Employee engagements
* Organization unit addresses

#### Employee conversion

The conversion file specifies in json how to map attributes from OS2mo to LDAP and from LDAP
to OS2mo, and takes the form:

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
when creating or updating an OS2mo object, and to take the class `user` when creating or
updating an LDAP object. If the LDAP schema uses a different class for the employee
object, specify that class here.

Each entry in the conversion file _must_ specify:
* An "objectClass" attribute.
    * OS2mo: Any OS2mo class from ramodels should be acceptable.
    * LDAP: Available LDAP classes and their attributes can be retrieved by calling
    [GET:LDAP_overview][get_overview].
* Attributes for all required fields in the OS2mo or LDAP class to be written
* For OS2mo classes: A link to the employee or organization unit's uuid must be present.

Note that all attributes MUST be accepted by the destination class in OS2mo or LDAP.
Exceptions for this are the LDAP `extensionAttribute` attributes. These attributes
can be present on LDAP classes, without being explicitly specified in the schema.

Also note that the application needs to be able to link OS2mo and LDAP objects to each
other.
See the chapter on [Linking LDAP and OS2mo objects](#link-ldap-and-os2mo-objects)

Values in the json structure may be normal strings, or a string containing one or more
jinja2 templates, to be used for extracting values. For example:

```
  [...]
  "mo_to_ldap": {
    "Employee": {
      "objectClass": "user",
      "__export_to_ldap__": true,
      "employeeID": "{{mo_employee.cpr_no}}"
    }
  }
  [...]
```
Here, `employeeID` in the resulting LDAP object will be set to the `cpr_no` value from
the OS2mo object. The `mo_employee` object will be added to the template context by adding
to the `mo_object_dict` in `mo_import_export.main.listen_to_changes_in_employees`.

More advanced template strings may be constructed, such as:
```
  [...]
  "ldap_to_mo": {
    "Employee": {
      "objectClass": "user",
      "__import_to_mo__": true,
      "givenname": "{{ldap.givenName or ldap.name|splitlast|first}}",
      "uuid": "{{ employee_uuid or NONE }}"
    }
  }
  [...]
```
Here, the OS2mo object's `givenname` attribute will be set to the givenName attribute from
LDAP, if it exists, or if it does not, to the name attribute modified to be split by the
last space and using the first part of the result. Note also the `uuid` field, which
must be present to map the employee to the proper object in OS2mo. In this case, the
uuid attribute links to a [global](#filters-and-globals) variable called `employee_uuid`.

Note that you can also choose not to export this information to LDAP, by setting 
`__export_to_ldap__` equal to `false`. Similarly, you can choose not to import any information
into OS2mo by setting `__import_to_mo__` equal to `false`

#### Address conversion

OS2mo can contain multiple addresses of the same type for a single user. It is therefore
recommended that the LDAP field corresponding to OS2mo's address value can contain multiple
values. If this is not the case, the address in LDAP will be overwritten every time a
new address of an existing type is added in OS2mo. Information about whether an LDAP field
can contain multiple values, can be found by calling [GET:LDAP_overview][get_overview].
and inspecting the `single_value` attribute.

An example of an address conversion dict is as follows:

```
  [...]
  "mo_to_ldap": {
    "EmailEmployee": {
      "objectClass": "user",
      "__export_to_ldap__": true,
      "mail": "{{mo_address.value}}",
      "employeeID": "{{mo_employee.cpr_no}}"
    }
  }
  [...]
```

Note that the `Email` key must be a
valid OS2mo address type name. OS2mo address types can be retrieved by calling
[GET:MO/Address_types_employee][get_employee_address_types].
In this example, it is recommended that
LDAP's `mail` attribute is a multi-value field.

Converting the other way around can be done as follows:

```
  [...]
  "ldap_to_mo": {
    "EmailEmployee": {
      "objectClass": "ramodels.mo.details.address.Address",
      "__import_to_mo__": true,
      "value": "{{ldap.mail or None}}",
      "type": "address",
      "validity": "{{ dict(from_date = ldap.mail_validity_from or now()|mo_datestring) }}",
      "address_type": "{{ dict(uuid=get_employee_address_type_uuid('EmailEmployee')) }}",
      "person": "{{ dict(uuid=employee_uuid or NONE) }}"
    },
  }
  [...]
```

Note the `address_type` field. This attribute must contain a dict, as specified by
`ramodels.mo.details.address.Address`. Furthermore the uuid must be a valid address type
uuid. Valid address type uuids can be obtained by calling
[GET:MO/Address_types_employee][get_employee_address_types] or by using the
`get_employee_address_type_uuid` [global](#filters-and-globals) function
in the template.

Furthermore, the object must contain a `person` entry, which refers to the employee uuid
for this which address is to be imported. In this example, we use the `employee_uuid`
[global](#filters-and-globals) variable.


##### Post Address conversion

For post addresses, it is required to use an address type in OS2mo with `scope` != `DAR`.
The reason for this is that we cannot expect an LDAP server to have the same address
format as DAR. The scope of address types in OS2mo can be retrieved using
[GET:MO/Address_types_employee][get_employee_address_types]
and [GET:MO/Address_types_org_unit][get_org_unit_address_types].

##### Organization unit address conversion

An address in an OS2mo organizational unit maps to every LDAP employee object who is
engaged at the organizational unit. This can be set up as follows:

```
  [...]
  "mo_to_ldap": {
    "LocationUnit": {
      "objectClass": "user",
      "__export_to_ldap__": true,
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
      "__import_to_mo__": true,
      "value": "{{ ldap.postalAddress or NONE }}",
      "type": "address",
      "validity": "{{ dict(from_date=now()|mo_datestring) }}",
      "address_type": "{{ dict(uuid=get_org_unit_address_type_uuid('LocationUnit')) }}",
      "org_unit": "{{ dict(uuid=get_or_create_org_unit_uuid(ldap.division)) }}"
    },
  }
  [...]
```

Note that an organizational unit address needs to have an `org_unit` attribute. In
contrast to an employee object, which needs a `person` attribute. For details regarding
`get_org_unit_path_string` and `get_or_create_org_unit_uuid`, see the chapter on
[engagement conversion](#engagement-conversion).

Mapping org unit addresses to LDAP objects other than `employee` objects (i.e. the
object which contains the address also contains employee information like name, cpr-no,
etc.) is currently not supported.

#### IT user conversion
It user conversion follows the same logic as address conversion. An example of an IT
user conversion dict is as follows:

```
  [...]
  "mo_to_ldap": {
    "Active Directory": {
      "objectClass": "user",
      "__export_to_ldap__": true,
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
      "__import_to_mo__": true,
      "user_key": "{{ ldap.msSFU30Name or None }}",
      "itsystem": "{{ dict(uuid=get_it_system_uuid('Active Directory')) }}",
      "validity": "{{ dict(from_date=now()|mo_datestring) }}",
      "person": "{{ dict(uuid=employee_uuid or NONE) }}"
    }
  }
  [...]
```

Note that we have specified the json key equal to `Active Directory`. This key needs
to be an IT system user key in OS2mo. IT system user keys can be retrieved using
[GET:MO/IT_systems][get_it_systems].

#### Engagement conversion
Engagement conversion follows the same logic as address conversion. An example of
an engagement conversion dict is as follows:

```
  [...]
  "mo_to_ldap": {
    "Engagement" : {
      "objectClass": "user",
      "__export_to_ldap__": true,
      "employeeID": "{{mo_employee.cpr_no}}",
      "department": "{{NONE}}",
      "company": "{{NONE}}",
      "departmentNumber": "{{mo_engagement.user_key}}",
      "division": "{{get_org_unit_path_string(mo_engagement.org_unit.uuid)}}",
      "primaryGroupID": "{{NONE}}",
      "employeeType": "{{get_engagement_type_user_key(mo_engagement.engagement_type.uuid)}}",
      "memberOf": "{{NONE}}",
      "personalTitle": "{{NONE}}",
      "title": "{{get_job_function_user_key(mo_engagement.job_function.uuid)}}"
    }
  }
  [...]
```

Note the `get_org_unit_path_string` function which we use for `ldap.division`. This will
write full organizational paths to ldap, rather than just the name of an organizational
unit. The organizational unit path is separated by the character specified in the
`ORG_UNIT_PATH_STRING_SEPARATOR` environment variable.

Converting the other way around can be done like this:

```
  [...]
  "ldap_to_mo": {
    "Engagement": {
      "objectClass": "ramodels.mo.details.engagement.Engagement",
      "__import_to_mo__": true,
      "org_unit": "{{ dict(uuid=get_or_create_org_unit_uuid(ldap.division)) }}",
      "job_function": "{{ dict(uuid=get_job_function_uuid(ldap.title)) }}",
      "engagement_type": "{{ dict(uuid=get_engagement_type_uuid(ldap.employeeType)) }}",
      "user_key": "{{ ldap.departmentNumber or uuid4() }}",
      "validity": "{{ dict(from_date=now()|mo_datestring) }}",
      "person": "{{ dict(uuid=employee_uuid or NONE) }}",
      "primary": "{{ dict(uuid=get_primary_type_uuid('primary')) }}"
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

Note the `primary` attribute. If you want, you can set this to a dictionary with an
uuid that refers to OS2mo's `primary` class. `primary` is not just a True/False value,
but can contain entries like for example `primary`, `not-primary`, `explicitly-primary`.
To inspect all possible values, which the `primary` class can take, use
[GET:MO/Primary_types][get_primary_types].

#### Link LDAP and OS2mo objects

For us to be able to synchronize objects between OS2mo and LDAP, we need to know which
LDAP user corresponds to which OS2mo user, and the other way around. This can be done
in two ways and is attempted in the following order:

* Using a properly configured IT-user
* Using cpr-number lookup

Both methods are described in this chapter.

##### Using a properly configured IT-user

If an OS2mo employee has an IT-user which contains the LDAP `distinguishedName` attribute
value, this is used to determine which LDAP object an OS2mo object corresponds to.
This method will succeed if:

* An IT-system is configured in the mapping file to contain LDAP's `distinguishedName`
  attribute as its `user_key`.
* The OS2mo user has exactly one IT-user of this type.

This can be configured in the file mapping as follows:

```
  [...]
  "mo_to_ldap": {
    "Active Directory": {
      "objectClass": "user",
      "__export_to_ldap__": true,
      "distinguishedName" : "{{mo_employee_it_user.user_key}}",
    },
  }
  [...]
```

And the other way around:

```
  [...]
  "ldap_to_mo": {
    "Active Directory": {
      "objectClass": "ramodels.mo.details.it_system.ITUser",
      "__import_to_mo__": true,
      "user_key": "{{ ldap.distinguishedName }}",
      "itsystem": "{{ dict(uuid=get_it_system_uuid('Active Directory')) }}",
      "validity": "{{ dict(from_date=now()|mo_datestring) }}",
      "person": "{{ dict(uuid=employee_uuid or NONE) }}"
    }
  }
  [...]
```

If an OS2mo employee does not have an IT-user (and also no cpr-number), a username is
generated for the employee, and uploaded as an it-system.

If an OS2mo employee has multiple IT-users with valid `distinguishedName` values,
an exception is raised.

##### Using cpr-number lookup

A cpr-number is unique to a person, and can therefore be used to look up the LDAP object
corresponding to an OS2mo employee. If the cpr-number is configured in the mapping file,
this is automatically attempted if the IT-user lookup fails or is not configured
(properly).

This required an employee to be configured as follows in the mapping file:

```
  [...]
  "mo_to_ldap": {
    "Employee": {
      "objectClass": "user",
      "__export_to_ldap__": true,
      "employeeID": "{{mo_employee.cpr_no}}",
      [...]
    },
  }
  [...]
```

And the other way around:

```
  [...]
  "ldap_to_mo": {
    "Employee": {
      "objectClass": "ramodels.mo.employee.Employee",
      "__import_to_mo__": true,
      "cpr_no": "{{ldap.employeeID|strip_non_digits}}",
      "uuid": "{{ employee_uuid or NONE }}"
      [...]
    },
  }
  [...]
```

Note that the OS2mo `employee.cpr_no` attribute is mapped both in the `ldap_to_mo` and
the `mo_to_ldap` mapping. This will cause the application to understand that it can
attempt a cpr-number lookup to find a matching object in LDAP/MO when required.

If LDAP contains multiple users with the same cpr-number, an exception is raised.

If LDAP does not contain any objects with the cpr-number of the OS2mo employee,
a username is generated and the LDAP object is created.


#### Filters and globals

In addition to the [Jinja2's builtin filters][jinja2_filters],
the following filters are available:

* `splitfirst`: Splits a string at the first space, returning two elements
  This is convenient for splitting a name into a givenName and a surname
  and works for names with no spaces (surname will then be empty). Takes a single
  separator argument which defaults to a whitespace. For example, you can write:
  `"streetAddress": "{{mo_org_unit_address.value|splitlast(',')|first|trim}}"`
* `splitlast`: Splits a string at the last space, returning two elements
  This is convenient for splitting a name into a givenName and a surname
  and works for names with no spaces (givenname will then be empty). Takes a single
  separator argument which defaults to a whitespace.
* `mo_datestring`: Accepts a datetime object and formats it as a string.
* `strip_non_digits`: Removes all but digits from a string.
* `parse_datetime`: Converts a date string to a datetime object. The year needs to be
  first. For example `2021-01-01`.

In addition to filters, a few methods have been made available for the templates.
These are called using the normal function call syntax. For example:
```
{
  "key": "{{ nonejoin(ldap.postalCode, ldap.streetAddress) }}"
}
```
* `now`: Returns current datetime
* `nonejoin`: Joins two or more strings together with comma, omitting any Falsy values
  (`None`, `""`, `0`, `False`, `{}` or `[]`)
* `get_employee_address_type_uuid`: Returns the address type uuid for an employee
  address type user_key
* `get_org_unit_address_type_uuid`: Returns the address type uuid for an org-unit
  address type user_key
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
* `get_engagement_type_user_key`: Returns the name of an engagement type, given its uuid
* `get_job_function_user_key`: Returns the name of a job function, given its uuid

Finally, the following global variables can be used:

* `employee_uuid`: uuid of the employee matching the converted object's cpr number.
  Can only be used in `ldap_to_mo` mapping.

#### Username generation
If a user is created in OS2mo, the tool will try to find the matching user in LDAP using
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


#### CRON jobs
The application is configured with three CRON jobs, which run on a periodic schedule:

* Daily at 23:00: Info dictionaries are reloaded by calling
  [POST:/reload_info_dicts][post_reload_info_dicts]. This is necessary, in case new
  object types are added to OS2mo. For example by using `OS2mo init`.
* Daily at 03:00: Objects which enter or leave validity are exported to the LDAP
  database by calling [POST:/synchronize_todays_events][post_synchronize_todays_events].


[swagger]:http://localhost:8000/docs
[get_overview]:http://localhost:8000/docs#/LDAP/load_overview_from_LDAP_LDAP_overview_get
[get_employee_address_types]:http://localhost:8000/docs#/MO/load_employee_address_types_from_MO_MO_Address_types_employee_get
[get_org_unit_address_types]:http://localhost:8000/docs#/MO/load_org_unit_address_types_from_MO_MO_Address_types_org_unit_get
[get_it_systems]:http://localhost:8000/docs#/MO/load_it_systems_from_MO_MO_IT_systems_get
[get_primary_types]:http://localhost:8000/docs#/MO/load_primary_types_from_MO_MO_Primary_types_get
[post_reload_info_dicts]:http://localhost:8000/docs#/Maintenance/reload_info_dicts_reload_info_dicts_post
[get_import_all]:http://localhost:8000/docs#/Import/import_all_objects_from_LDAP_Import_all_get
[get_import_single]:http://localhost:8000/docs#/Import/import_single_user_from_LDAP_Import__dn__get
[post_synchronize_todays_events]:http://localhost:8000/docs#/Maintenance/synchronize_todays_events_Synchronize_todays_events_post
[jinja2_filters]:https://jinja.palletsprojects.com/en/3.1.x/templates/#builtin-filters
[post_export_all]:http://localhost:8000/docs#/Export/export_mo_objects_Export_post
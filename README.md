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

First create a `docker-compose.override.yml` file based on the
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
      "validity": "{{ dict(from_date = ldap.mail_validity_from or now()|strftime) }}",
      "address_type": "{{ dict(uuid='f376deb8-4743-4ca6-a047-3241de8fe9d2') }}"
    },
  }
  [...]
```

Note the uuid in the `address_type` field. This value must be a dict, as specified by
`ramodels.mo.details.address.Address`. Furthermore the uuid must be a valid address type
uuid. Valid address type uuids can be obtained by calling
[GET:MO/Address_types][get_address_types].


#### Filters and globals

In addition to the [Jinja2's builtin filters][jinja2_filters],
the following filters are available:

* `splitfirst`: Splits a string at the first space, returning two elements
  This is convenient for splitting a name into a givenName and a surname
  and works for names with no spaces (surname will then be empty)
* `splitlast`: Splits a string at the last space, returning two elements
  This is convenient for splitting a name into a givenName and a surname
  and works for names with no spaces (givenname will then be empty)
* `strftime`: Accepts a datetime object and formats it as a string

In addition to filters, a few methods have been made available for the templates.
These are called using the normal function call syntax:
```
{
  "key": "{{ nonejoin(ldap.postalCode, ldap.streetAddress) }}"
}
```
* `nonejoin`: Joins two or more strings together with comma, omitting any Falsy values 
  (`None`, `""`, `0`, `False`, `{}` or `[]`)
* `now`: Returns current datetime

[swagger]:http://localhost:8000/docs
[get_overview]:http://localhost:8000/docs#/LDAP/load_overview_from_LDAP_LDAP_overview_get
[get_address_types]:http://localhost:8000/docs#/MO/load_address_types_from_MO_MO_Address_types_get
[jinja2_filters]:https://jinja.palletsprojects.com/en/3.1.x/templates/#builtin-filters
---
title: Integration abstraction
---

A small library to easy the use of the *integrationsdata*
field in LoRa.

The utility provides functionality to read and write fields from the
integration data stored with an object, while taking care of not
overwriting other keys stored by other integrations on the same object.

The utility also provides basic functionality to find objects based on
their integration data.

## Usage

Import the utility, eg: :

``` python
from integration_abstraction.integration_abstraction import IntegrationAbstraction
```

The tool takes parameters for *system_name* and
*end_marker*. *system_name* is the name of the
key that will be used for the current session, the utility will take of
abstracting away the underlying json-structure that is actually stored
in the *integrationsdata* field, and will only presnet the
user with the values associated with the key chosen by
*system_name*.

*end_marker* is the value that is appeded to all values to
ensure that it is possible to uniquely find objects despite the fact
that structured search is not avaiable for integration data in LoRa. The
value defaults to STOP. If this word could potentially be bart of the
actual stored value, another *end_marker* should be chosen.

## Writing and reading Integration Data

To write integration data to an object: :

``` python
mox_base = 'http://localhost:8080'
resource = '/klassifikation/facet'
uuid = '00000000-0000-0000-0000-000000000001'

set_value = 'Rose Bowl 101'
ia = IntegrationAbstraction(mox_base, 'AD', 'STOP')
ia.write_integration_data(resource, uuid, set_value)
```

The data will be written to the objects *integrations_data*
field while all other keys will be left untouched.

To read back he value:

```
read_value ia.write_integration_data(resource, uuid)
```

## Complex data

It is to some degree possible to store more complex data structures. The
data is stored as JSON, and thus dictionaries can be stored, as long as
keys are strings: :

```python
set_value = {'a': 'klaf', 'b': 3, 'c': {'a': 1, 'b': 2, '5': {'def': 9}}}
ia.write_integration_data(resource, uuid, set_value)
```

The values must be json-serializable and thus it is not possible to
store more complex structures like Python pickle objects.

## Searching

It is possible to find objects based on their integration data value,
provided that the vaulue does not contain characters that are considred
special by the underlying search engnine in
[LoRa](https://github.com/magenta-aps/mox/blob/95adfd192a729d6a82b08b2188dbda77522b881b/doc/dev/wildcards.rst),
ie avoid characters such as `%`, `&`, `''` and `_` if the object
should be found in a search.

It is not possible to easily find more complex objects like dictionaries
in a search.

To find a object with integration data value 'AndyFl': :

``` python
value = 'AndyFl'

# Write the value
ia.write_integration_data(resource, uuid, value)

# Find the object
uuid = ia.find_object(resource, value)
```

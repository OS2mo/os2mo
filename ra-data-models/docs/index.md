<!--
SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->

# RA Data Models Documentation

Models used by [OS2mo](https://github.com/OS2mo/os2mo). This project is available on [PyPI](https://pypi.org/project/ramodels/).

## Requirements

Python 3.8+

Dependencies:

- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [backports.zoneinfo](https://pypi.org/project/backports.zoneinfo/) for Python <3.9

## Installation

Install via pip

```bash
pip install ramodels
```

or use as a dependency in your own project via e.g. [Poetry](https://python-poetry.org/)

```bash
poetry add ramodels
```

## Usage

Create POST payloads to OS2mo. For example:

```python
from ramodels.mo import OrganisationUnit

new_ou = OrganisationUnit(
    user_key="Unit 1337",
    name="My Awesome Org Unit",
    org_unit_type={"uuid": "unit_type_uuid"},
    org_unit_level={"uuid": "level_uuid"},
    validity={"from": "2021-10-06"},
)
print(new_ou.json(by_alias=True, indent=2))
# >>>
# {
#   "uuid": "f4937c3b-1b88-4182-a77d-a57bafdce347",
#   "type": "org_unit",
#   "user_key": "Unit 1337",
#   "validity": {
#     "from_date": "2021-10-06T00:00:00+02:00",
#     "to_date": null
#   },
#   "name": "My Awesome Org Unit",
#   "parent": null,
#   "org_unit_hierarchy": null,
#   "org_unit_type": {
#     "uuid": "unit_type_uuid"
#   },
#   "org_unit_level": {
#     "uuid": "level_uuid"
#   }
# }
```

## License

This project is licensed under the terms of the [MPL-2.0 license](https://www.mozilla.org/en-US/MPL/2.0/).

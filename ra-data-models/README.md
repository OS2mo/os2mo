<!--
SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
SPDX-License-Identifier: MPL-2.0
-->


# MoLoRa Data Models

RAModels - MoLoRa data validation models powered by [pydantic](https://github.com/samuelcolvin/pydantic/#pydantic).

## Versioning
This project uses [Semantic Versioning](https://semver.org/) with the following strategy:
- MAJOR: Incompatible changes to existing data models
- MINOR: Backwards compatible updates to existing data models OR new models added
- PATCH: Backwards compatible bug fixes


## Authors

Magenta ApS <https://magenta.dk>

## License
- This project: [MPL-2.0](MPL-2.0.txt)
- Dependencies:
  - pydantic: [MIT](MIT.txt)

This project uses [REUSE](https://reuse.software) for licensing. All licenses can be found in the [LICENSES folder](LICENSES/) of the project.

## Development
### Prerequisites

- [Poetry](https://github.com/python-poetry/poetry)
- [Pre-commit](https://github.com/pre-commit/pre-commit)


### Getting Started

1. Clone the repository:
`git clone git@git.magenta.dk:rammearkitektur/ra-data-models.git`

2. Install all dependencies:
`poetry install`

3. Set up pre-commit:
`pre-commit install`


### Running the tests

You use `poetry` and `pytest` to run the tests:

`poetry run pytest`


You can also run specific files

`poetry run pytest tests/<test_folder>/<test_file.py>`

and even use filtering with `-k`

`poetry run pytest -k "Manager"`


You can use the flags `-vx` where `v` prints the test & `x` makes the test stop if any tests fails (Verbose, X-fail)

### Pre-commit usage
Pre-commit must either be used via your virtual environment or globally.
If you want to pre-commit globally, the following extra dependencies are needed:
`pip install mypy pydantic`


### Models

## LoRa
`LoRa` implements the OIO standard version 1.1. The [standard](https://digitaliser.dk/resource/1569113) with
[specification](https://www.digitaliser.dk/resource/1569113/artefact/Specifikationafserviceinterfacefororganisation-OIO-Godkendt%5bvs.1.1%5d.pdf?artefact=true&PID=1569586)

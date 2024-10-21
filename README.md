# OS2mo
MO is an IT system for organisational and identity management.

It enables your organisation to maintain information about the organisation and
its employees, volunteers, external consultants, robot users, and so on, from a
single user interface.

You get a complete overview of all departments, employees' (multiple)
employments, their IT access, their affiliations, and roles throughout the
organisation. You also get a complete picture of management hierarchies, and
you can see your union representative organisation, your payroll organisation,
your safety organisation, your line organisation, etc.

The vision for MO is that it should be *the* source system for the entire
organisation and its employees: this is where organisational changes are made,
this is where employees are created and removed, and this information will
automatically - and immediately - be sent to other systems. The information can
also come from other systems - or be enriched from them - but it is MO that
contains the complete picture of the organisation.

Because MO contains all the information about the organisation, and it is always
up-to-date and correct, it is important to connect MO to other systems that
need the information - be it LDAP (e.g. Active Directory), an IdM system,
FK-Organisation, an org chart, an HR system, etc.

When MO is connected to many systems, workflows are automated and consistent
and high data quality is realised in the connected systems.

The primary documentation for OS2mo is available at
<https://rammearkitektur.docs.magenta.dk/os2mo/index.html> (in Danish).
Technical documentation in English is available at
<https://rammearkitektur.docs.magenta.dk/os2mo/tech-docs/architecture.html>.


## GraphQL
The primary API for OS2mo is GraphQL. It is available at `/graphql`, e.g. for
local development: <http://localhost:5000/graphql>.

![graphiql](img/graphiql.png)

Note that GraphiQL has a built-in documentation-explorer which can be accessed
by ctrl-clicking most fields. More thorough documentation for the GraphQL API
is available at
<https://rammearkitektur.docs.magenta.dk/os2mo/tech-docs/graphql/intro.html>.

The GraphQL schema is exposed at `/graphql/vXX/schema.graphql` in regular
GraphQL Schema Definition Language (SDL).


## Getting Started
To get a local OS2mo stack running on a sane operating system:
```shell
git clone https://github.com/OS2mo/os2mo.git
cd os2mo/
docker compose up -d --build
```
The OS2mo frontend should now be available at <http://localhost:5000>, and the
GraphiQL explorer at <http://localhost:5000/graphql>. The default admin
username/password is `alvida`/`alvida`.

To stop the stack, run
```shell
docker compose down
```

To stop the stack _and delete all data volumes_, run
```shell
docker compose down -v
```

A more detailed walk-through is available at
<https://rammearkitektur.docs.magenta.dk/os2mo/tech-docs/development.html>.


## Versioning
This project uses [Semantic Versioning](https://semver.org/) with the following
strategy:
- MAJOR: Incompatible API changes.
- MINOR: Backwards-compatible updates and functionality.
- PATCH: Backwards-compatible bug fixes.

The changelog is available at
<https://rammearkitektur.docs.magenta.dk/os2mo/changelog.html>.


## Authors
Magenta ApS <https://magenta.dk>


## License
[MPL-2.0](LICENSES/MPL-2.0.txt). This project uses
[REUSE](https://reuse.software) for licensing. All licenses can be found in the
[LICENSES folder](LICENSES/) of the project.

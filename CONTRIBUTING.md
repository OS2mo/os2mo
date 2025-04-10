# Contributing to OS2mo

Welcome and thank you for your interest in contributing to OS2mo! We appreciate
your support.

## Getting Started

OS2mo encourages and welcomes new contributors. Our documentation contains
guidance for first-time contributors, including:

- [Getting Started](README.md#getting-started): Getting a local stack up and
  running.
- [Development](https://rammearkitektur.docs.magenta.dk/os2mo/tech-docs/development.html):
  A more detailed installation guide, including setup on exotic operating
  systems (Microsoft Windows).
- [GraphQL](README.md#graphql): A primer on the API.
- [Events](https://rammearkitektur.docs.magenta.dk/os2mo/tech-docs/events.html):
  A detailed overview of OS2mo's event system for integration developers.

The full documentation is available at <https://rammearkitektur.docs.magenta.dk/os2mo/>.

## Submitting Code Patches

The following applies to all OS2mo repositories, including OS2mo itself and all
of its integrations.

Before beginning your work, please search for related issues:

- <https://github.com/os2mo/os2mo/issues>
- <https://github.com/magenta-aps/os2mo/issues>
- <https://os2web.atlassian.net/projects/MO/issues>
- <https://redmine.magenta.dk/projects/rammearkitektur/issues>

Or existing patches:

- <https://github.com/os2mo/os2mo/pulls>
- <https://github.com/magenta-aps/os2mo/pulls>

If there are no relevant issues yet, and you are not sure whether your change
is likely to be accepted, consider opening an issue yourself. We strongly
recommend first-time contributors not submit large changes or features without
first consulting the maintainers.

Before requesting a code review, ensure your patch passes all CI checks
including [pre-commit](https://github.com/pre-commit/pre-commit) hooks (lint,
typing, etc.) and tests. Unit- and integration-tests can be executed locally in
the development environment using [pytest](https://docs.pytest.org):

```sh
# Run all tests
docker compose exec mo pytest

# Iterate on a single test
docker compose exec mo pytest backend/tests/graphapi/test_classes.py::test_integration_names_filter
```

## Integration Development

Don't write your integration as an hourly/daily/weekly batch job! Instead,
consider utilising OS2mo's [event
system](https://rammearkitektur.docs.magenta.dk/os2mo/tech-docs/events.html).

Most of the integrations in the ecosystem are available at
<https://github.com/orgs/OS2mo/repositories>. End-user friendly documentation
for most of OS2mo's integrations is available at
<https://rammearkitektur.docs.magenta.dk/os2mo/integrations/ldap_ad_amqp_integration.html>.

## Improving the Documentation

The documentation for OS2mo and most of its integrations is hosted on
<https://rammearkitektur.docs.magenta.dk/os2mo/>. The underlying source files
are located in [`docs/`](docs/). Changes to the documentation follow the same
procedure as any other code change.

## Reporting a Vulnerability

Check out the [security policy](SECURITY.md).

## Getting Help

Whenever you are stuck, or do not know how to proceed, you can always ask for
help. We invite you to use the discussions here on GitHub to ask questions.

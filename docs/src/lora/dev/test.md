---
title: Testing
---

The tests use the database user credentials defined in
[settings](../user/settings.md). It requires the
[CREATEDB](https://www.postgresql.org/docs/11.7/role-attributes.html)
privilege and
[OWNER](https://www.postgresql.org/docs/11.7/sql-alterdatabase.html) of
the database or have the
[SUPERUSER](https://www.postgresql.org/docs/11.7/role-attributes.html)
privilege to run the tests.

When tests are run, a pytest fixture ensures that tests use a separate
testing database. This testing database is usually named `mox_test`. The
testing database is created using the same credentials as the normal
`mox` database. The testing database is reset to a blank schema between
test runs.

When LoRa runs as a dependency of the MO unittest suite, the "testing
API" is used to setup, reset and tear down the testing database.

## Writing new tests

The `oio_rest/test/util.py` contains classes suitable for writing tests.
See the docstrings there for determining the proper testclass for your test.

The general naming convention for files containing tests is: if it does
not contain `integration`, it is not expected to need any external
resourses such as a database.

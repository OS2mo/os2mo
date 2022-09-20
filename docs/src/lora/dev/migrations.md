---
title: Database migrations
---

LoRa uses the Alembic migrations framework to manage database schema
migrations.

When LoRa is running as a Docker container, Alembic can be invoked like
this:

``` bash
$ docker-compose exec mox alembic <command>
```

E.g., to update the database schema to the latest available migration,
run:

``` bash
$ docker-compose exec mox alembic upgrade head
```

It is also possible to run Alembic outside of Docker. This is especially
useful when using Alembic commands which generate new files, as the
Docker container cannot write to the host filesystem by default. This
means that generating new migrations (which creates a file) can be done
using Poetry instead:

``` bash
DB_HOST=localhost DB_PORT=6543 DB_USER=postgres DB_PASSWORD=...
DB_NAME=mox poetry run alembic revision
```

(This presumes that the Postgres container has its port mapped to host
port 6543.)

## The testing database

Some of the tests in the LoRa test suite require reading and/or writing
to the database. To ensure that tests run in a separate testing
database, we use a pytest fixture `tests_setup_and_teardown` defined in
`conftest.py`. This fixture ensures that a separate testing database,
usually called `mox_test`, is created in the Postgres instance available
to LoRa.

The testing database is also used when the LoRa "testing API" is used.
Invoking the `/testing/db-setup` API creates a new testing database, if
it is not already there. `/testing/db-reset` and `/testing/db-teardown`
reset and tear down the testing database, respectively. This is used by
the MO test suite.

LoRa uses the Alembic migrations when setting up a testing database.

## Schema names

LoRa uses the database tables in the schema called "actual_state".

Alembic uses a database table called "alembic_version" to track what
migrations have been applied to a given database. This table is created
in the default Postgres schema ("public".) This ensures that if the
"actual_state" schema is dropped, the Alembic migration history
remains.

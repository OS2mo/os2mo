---
title: Database
---

This document describes what you need to do to prepare a database for
usage by `mox`. Generally, there are 2 steps. The first requires a high
level of privileges and creates a user. The second is within the
database and can be done by the created user. The 2 following
subchapters reflect these two levels of privilege.

Database, user and extensions initialization {#db_user_ext_init}
============================================

`mox` requires a database and a user in that database. You can configure
the name of the database and user a running `mox` will use in
`settings`{.interpreted-text role="ref"} under the
[\[database\]]{.title-ref} heading. The user should have [all
privileges](https://www.postgresql.org/docs/11.7/sql-grant.html) on the
database. Furthermore, there should be a schema in the database called
[actual\_state]{.title-ref} that the user has authorization over. At
last, the search path should be set to [\"actual\_state,
public\"]{.title-ref}. Please refer to the reference script
`docker/postgres-initdb.d/10-init-db.sh`{.interpreted-text role="file"}.

There is one more thing `mox` needs before it can work with the
database: **extensions**. The required extensions are *uuid-ossp*,
*btree\_gist* and *pg\_trgm* and they should be created with the schema
[actual\_state]{.title-ref}. Note that extensions can only be created by
a superuser (this is because extensions can run arbitrary code). Please
refer to the reference script
`docker/postgres-initdb.d/20-create-extensions.sh`{.interpreted-text
role="file"}.

Object initialization {#db_object_init}
=====================

With mox comes a utility called `initdb` that populates a Postgres
server database with all the necessary postgresql objects.

`initdb` is only intended to run succesfully against a database that has
been initialized as described in `db_user_ext_init`{.interpreted-text
role="ref"}.

To invoke `initdb`, run:

    python -m oio_rest initdb

Please also read `python -m oio_rest initdb --help`.

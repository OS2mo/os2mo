---
title: Settings
---

`oio_rest` has various configurable parameters. This file describes how
to configure the program. There are default settings, as shown in
`oio_rest/oio_rest/default-settings.toml`. These can be overwritten by two 
files that you can point to with environment variables:

1. MOX_SYSTEM_CONFIG_PATH

> Path to a toml settings file. This overwrites the default settings, 
but has lower precedens than `MOX_USER_CONFIG_PATH`. The purpose of 
this file is to configure environments. We use it for docker.

2. MOX_USER_CONFIG_PATH

> Point this to a toml file with your desired settings. The settings in 
this file has the highest precedens.

This is the content of
`oio_rest/oio_rest/default-settings.toml`:

``` toml
# endpoints such ``http://example.com/MyOIO/organisation/organisationenhed``.
base_url = ""


[database]
host = "localhost"
port = 5432
user = "mox"
password = "mox"
db_name = "mox"


[restrictions]
# Whether authorization is enabled.
# If not, the restrictions module is not called.
enable = false
# The module which implements the authorization restrictions.
# Must be present in sys.path.
module = "oio_rest.auth.wso_restrictions"
# The name of the function which retrieves the restrictions.
# Must be present in AUTH_RESTRICTION_MODULE and have the correct signature.
function = 'get_auth_restrictions'


[file_upload]
# This is where file uploads are stored. It must be readable and writable by
# the mox user, running the REST API server. This is used in the Dokument
# hierarchy.
folder = "/var/mox"


[audit_log]
host = ""
exchange = "mox.log"
queue = "mox.log_queue"
ignored_services = ["Log"]


[log]
activity_log_path = "activity.log"
log_path = "oio_rest.log"
log_level = "WARNING"


[testing_api]
# If enabled, expose /testing/db-* endpoint for setup, reset and teardown of a
# test database. Useful for integration tests from other components such as MO.
# Does not work when running multi-threaded.
enable = false


[truncate_api]
# If enabled, exposes /db/truncate endpoint, for truncating the current
# database.
enable = false

[search]
# If enabled, uses alternative search implementation
enable_quick_search = true
``` 
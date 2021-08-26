Release type: major

New features
------------
* #45211: Added commit shas and tags to docker images.
* #44082: Role-based access control (RBAC) for the organization part of the system. The feature is enabled via an ENV variable
* #43998: Rework docker-compose.yaml and made database-backing on confdb configurable.
* #44744: Cleaned up tags in the OpenAPI docs endpoint (/docs)
* #44744: Added keycloak support on the OpenAPI docs endpoint (/docs)
* #44717: Added confdb environment settings, adjusted confdb healthcheck, disabled set configuration endpoints
* #44746: Expanded AMQP events with service-uuid, cleanup in trigger module
* #43364: Added sslmode to database connection options
* #44187: Add structured logs. Improvements to debugging/troubleshooting
* #42774: Add English translation. The user can now choose Danish or English screen texts by clicking the flags in the nav bar
* #42869: Added delta-api parameter "changed_since" to /api/v1/ endpoints
* #43544: Keycloak authentication. Keycloak container, DB and config added
* #41560: New org-funk: Owners
* #44181: Add Opentelemetry instrumentation
* #43364: Reimplement settings using Pydantic and environment variables
* #37599: Users can now terminate organisation unit registrations (as an alternative to terminating the entire organisation unit)
* #44188: Add local Grafana/OpenTelemetry development environment (:3000/explore)
* #44596: Implement Prometheus FastAPI instrumentor, new metrics endpoint with version and health checks
* #38239: Users can now search on more properties of employees and organisation units.
* #39858: Users can now see additional properties of employees and organisation units in the search results, if configured.
* #44530: Speed up the search for matching organisation units from the "org unit picker", if configured.

Bug fixes
---------

* #44674: Editing an organisation unit's start date caused the wrong start date to be used

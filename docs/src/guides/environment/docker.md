# Docker Environment

## Getting Started
OS2mo is primarily developed using [Docker](https://www.docker.com/). Follow the
[official installation guide](https://docs.docker.com/engine/install/) for your operating system to set it up. It is
recommended to enable [managing Docker as a non-root user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
to ease usage.

Additionally, distributed development of the application is empowered through the use of the [git](https://git-scm.com/)
version control system. It should also be [installed](https://git-scm.com/downloads) for any developer who wishes to
contribute to the project.

After installing the required dependencies, the OS2mo development stack, and all necessary services, can be started by
executing the following commands:
```bash
git clone git@git.magenta.dk:rammearkitektur/os2mo.git  # or https://github.com/OS2mo/os2mo.git
cd os2mo
docker-compose up -d --build
```

This starts the following services:

 - OS2mo frontend: http://localhost:5001.
 - OS2mo backend: http://localhost:5000.
 - LoRa: http://localhost:8080.
 - Keycloak: http://localhost:8081/auth/admin/.
 - Grafana: http://localhost:3000.

The `-d` flag runs the services in the background; to see the output of a container, run `docker-compose logs <name>`,
where `<name>` is the name of the service from `docker-compose.yml`. Furthermore, the `backend/` directory on the host
machine is mounted into the OS2mo backend container, which enables automatic reloading of the server on changes to the
code.

Development of the frontend code should be done using the OS2mo frontend service on port `5001`, as changes to the
`frontend/` directory are automatically reloaded using `vue-cli-service serve`. The frontend container proxies all API
requests to the backend.

To bring down the stack, run
```bash
docker-compose down
```
which stops the services but persists the data. Add the `-v` flag to also remove all data.


## Feature Flags
Customising the behaviour of the application is primarily done through _feature flags_, which are implemented through
[environment variables](https://12factor.net/config). To add or change environment variables, the file
`docker-compose.override.yml` is used. This optional file is developer-specific, and therefore not versioned in git,
and is [read by default](https://docs.docker.com/compose/extends/) when using `docker-compose up`. The override file,
as its name implies, can contain configuration overrides for existing services or entirely new services. If a service is
defined in both the override and main `docker-compose.yml` files, `docker-compose`
[merges](https://docs.docker.com/compose/extends/#adding-and-overriding-configuration) the configurations.

As an example, this functionality can be used to disable authentication for OS2mo by creating a file
`docker-compose.override.yml` with the following content:
```yaml
services:
  mo:
    environment:
      OS2MO_AUTH: "false"
```

## Importing Fixture Data
By default, the OS2mo instance is completely void of any data. To encourage play, fixture data can easily be loaded into
the application by augmenting the startup command as follows:
```bash
# Stop the stack, removing any attached volumes
docker-compose down -v

# Start the stack, loading the 'kolding' fixture dataset of approximately 900 employees
FIXTURE=kolding docker-compose -f docker-compose.yml -f docker-compose.fixture.yml [-f docker-compose.override.yml] up -d --build
```
If the `FIXTURE` environment variable is unset, the default `kolding` fixture will be used. For a list of supported
fixtures, see the [OS2mo Fixture Loader repo](https://git.magenta.dk/rammearkitektur/os2mo-fixture-loader). Note that
`-f docker-compose.override.yml` is optional, and should only be set if such configuration is used.


## Troubleshooting

### Docker Compose Timeout
**Problem**: `docker-compose up` fails with something resembling
```
ERROR: for os2mo_frontend_1
UnixHTTPConnectionPool(host='localhost', port=None): Read timed out.
(read timeout=60)
```
**Possible solution**: Adjust the environment variable `COMPOSE_HTTP_TIMEOUT` as follows:
```bash
env COMPOSE_HTTP_TIMEOUT=300 docker-compose up -d --build
```

Alternatively, add the configuration to `.env` for future use:
```bash
echo 'COMPOSE_HTTP_TIMEOUT=300' >> .env
```

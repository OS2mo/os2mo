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

## Debugging

### VSCode

In order to use breakpoints in VSCode while developing OS2Mo, a `.vscode/launch.json` and `.vscode/tasks.json` file is required. The launch file is for starting the debugger, but since the debugger needs a docker-container to run, we have a tasks file as well, which the launch files specifies as a requirement for it to run. In this file we specify two tasks: how to build the docker-container & how to run it.

**.vscode/launch.json:**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Docker: Python - Fastapi",
            "type": "docker",
            "request": "launch",
            "preLaunchTask": "docker-run: debug",
            "python": {
                "pathMappings": [
                    {
                        "localRoot": "${workspaceFolder}",
                        "remoteRoot": "/app"
                    }
                ],
                "projectType": "fastapi"
            }
        }
    ]
}
```

**.vscode/tasks.json:**

```json
{
	"version": "2.0.0",
	"tasks": [
		{
			"type": "docker-build",
			"label": "docker-build",
			"platform": "python",
			"dockerBuild": {
				"tag": "os2mo:latest",
				"dockerfile": "${workspaceFolder}/docker/api.Dockerfile",
				"context": "${workspaceFolder}",
				"pull": true
			}
		},
		{
			"type": "docker-run",
			"label": "docker-run: debug",
			"dependsOn": [
				"docker-build"
			],
			"python": {
				"args": [
					"--factory",
					"mora.app:create_app",
					"--reload",
					"--host",
					"0.0.0.0",
					"--port",
					"80",
					"--log-level",
					"info"
				],
				"module": "uvicorn"
			},
			"dockerRun": {
				"envFiles": [
					"${workspaceFolder}/dev-environment/os2mo.env"
				],
				"network": "os2mo_default",
				"networkAlias": "mo"
			}
		}
	]
}
```

A lot of these configurations can be auto-generated using the vscode option: "**Docker: Initialize for Docker debugging**". The two files shown above will then be generated, but will not work out of the box, due to os2mo's file structure. To fix this we only need to update the `tasks.json`-file, since the auto-generated launch file is fine.

The following changes have been made to above files

* Fixed path to docker file, from `${workspaceFolder}/Dockerfile` to `${workspaceFolder}/docker/api.Dockerfile` in `<docker-build-task>`
* Change `<docker-run-task>.python.args`, so the following will be executed: `uvicorn --factory mora.app:create_app --reload --host 0.0.0.0 --port 80 --log-level info`
* Added entire `dockerRun` part to the `<docker-run-task>`
  * Network added due to our reverse proxy using docker-container-names.
  * NetworkAlias is so the docker-container created for debugging will take this network name, so the reverse-proxy hits the correct container.
    * OBS: I started my container up while my old container `mo-1` was still running. It didn't seem to be a problem, but to be sure, i stopped that container. So now i am sure the reverse proxy always directs me to the debugging-container.



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

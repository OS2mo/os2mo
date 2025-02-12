# Development

OS2mo is primarily developed using [Docker](https://www.docker.com/). Follow
the [official installation guide](https://docs.docker.com/engine/install/) for
your operating system to set it up. It is recommended to enable [managing
Docker as a non-root
user](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)
to ease usage.

Additionally, distributed development of the application is empowered through
the use of the [git](https://git-scm.com/) version control system. It should
also be [installed](https://git-scm.com/downloads) for any developer who wishes
to contribute to the project.

After installing the required dependencies, the OS2mo development stack, and
all necessary services, can be started by executing the following commands:

```shell
git clone https://github.com/OS2mo/os2mo.git
cd os2mo/
docker compose up -d --build
```

The full list of services can be inspected with `docker compose ps` or by
reading `docker-compose.yml`. The most important thing to begin with is that
you can visit <http://localhost:5000> in your browser. Before getting access to
OS2mo, you will be redirected to Keycloak where you can sign in as `alvida`
with the password `alvida`. The GraphQL API explorer (GraphiQL) is available at
<http://localhost:5000/graphql>.

The `-d` flag for `docker compose up` runs the services in the background. To
see the output of a container, run `docker compose logs <name>`, where `<name>`
is the name of the service from `docker-compose.yml`. Furthermore, the
`backend/` directory on the host machine is mounted into the OS2mo backend
container, which enables automatic reloading when the code is changed.

To bring down the stack, run `docker compose down`, which stops the services
but persists the data. Add the `-v` flag to remove all
data.

## Microsoft Windows

If you really want to, OS2mo can be run on Windows through [Windows Subsystem
for Linux](https://learn.microsoft.com/en-us/windows/wsl/) (WSL). **Because the
development stack mounts files from the host into the container, the OS2mo repo
must be cloned _inside_ WSL**.

After [installing WSL](https://learn.microsoft.com/en-us/windows/wsl/install),
launch the "Ubuntu" program from the Windows start menu to get a shell.

Even though we will **not** be using Docker Desktop, it may have installed the
docker CLI in Ubuntu for you. Check if docker is installed:

```shell
docker --version
```

Install docker if it is **not** already installed, otherwise skip this step:

```shell
sudo apt update
sudo apt install docker.io docker-buildx docker-compose-v2
```

The OS2mo development stack can now be started by following the instructions
[above](#Development).

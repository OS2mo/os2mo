Release type: patch

Install poetry in a isolated environment

This fixes build problems where poetry changes the dependencies for poetry
itself when installing packages.

This also cleans up the `Dockerfile` for various rot.

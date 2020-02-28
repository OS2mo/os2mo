Conventions
===========

This section contains the various conventions, standards and workflows used in this project

Git workflow
------------

The project is developed using `Git flow <https://nvie.com/posts/a-successful-git-branching-model/>`_

General conventions
"""""""""""""""""""

All commit messages must start with the Redmine ticket ID on the following form:

.. code-block:: none

    [#32608] Implement feature X

    ...

This allows easy traceability between a given commit and the Redmine
issue from which the commit originates.

Development/bugfixing
"""""""""""""""""""""

- Feature and bugfix branches are based on ``development``.
- Once a feature/bugfix is complete, a Merge Request should be opened on Gitlab
- Be sure to follow the associated MR template!

Releasing
"""""""""

- Create a ticket in Redmine for the current release (if one doesn't exist)
- Create a release branch for the release, according to Git flow, e.g. ``release/1.0.0``
- Bump the version in ``package.json`` and ``backend/__init__.py`` according to Semantic Versioning. Conventionally, these two version numbers always match.
- Update ``NEWS.rst`` with new version number and date.
- Once these changes have been made, and the release branch has been pushed to Gitlab, the usual CI checks will be performed and a Docker image will be created with the tag ``magentaaps/os2mo:rc``
  - Note that this tag is overwritten whenever a release branch is built, always pointing to the _newest_ release candidate.
- Deploy the release candidate to a testing server.
- Perform manual testing of the release, and verify that it doesn't contain any breaking bugs or regressions.
- Create a pull request from the release branch to ``master``. The review should focus primarily on the few changes made during the release process, e.g. bumping the version and finalizing the release notes. All other changes have already gone through review once. Do not delete the release branch yet!
- Create a tag on the merge commit on ``master`` with the version number on the form ``X.Y.Z``, and push it to Gitlab. This will initiate the release process and cause Gitlab CI create a Docker image tagged with the version number, i.e. ``magentaaps/os2mo:X.Y.Z``
- Finally, create a pull request from the release branch to ``development``. Delete the release branch.

Continuous Integration
----------------------

We use Gitlab CI for continuous integration.
Whenever a commit is pushed to Gitlab a job is created in the associated `CI pipeline
<https://git.magenta.dk/rammearkitektur/os2mo/pipelines>`_.

The pipeline first ensures that the code quality is consistent, and that everything builds without problems.

Once the first phase is passed, the tests are run on the newly built Docker image.

Once the tests pass, we tag and push the Docker image on the following conditions:

- Builds from ``development`` are tagged with ``magentaaps/os2mo:dev``
- Builds from release branches (``release/X.Y.Z``) are tagged with ``magentaaps/os2mo:rc``
- Builds of tagged commits, following a merge to ``master`` are tagged with ``magentaaps/os2mo:X.Y.Z`` and ``magentaaps:os2mo:latest``

To see a full overview of all the various checks in the pipeline, refer to ``.gitlab-ci.yml`` in the root of the repository.

Code standards
--------------

In the Python code we follow and enforce `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ through `Flake8 <https://flake8.pycqa.org/en/latest/>`_.
Additionally, we follow and enforce the `Flake8 Bugbear rules <https://github.com/PyCQA/flake8-bugbear>`_

Dependencies
------------

Dependencies for Python projects are managed through `pip-tools <https://github.com/jazzband/pip-tools>`_.

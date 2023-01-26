---
title: Testsuite
---

## How to write tests

### Test categories

! Not all tests currently adhere to this standard. However this should be the standard:

| Category | Scope | Limitations | Speed  |
|----------| :-------------:|:------:|----:|
| Unit | Assert that an action i completed correctly within a single module | No db, no network, no other system dependencies, should be able to be run without a container | 100 ms|
| Integration - narrow | Test how a single module interacts with one other module | A max of one dependency (ie. a database OR a webserver ) | ~500 ms |
| Integration - broad | Asserts that an action behaves correctly through multiple modules | No limits, except it should not communicate with other services outside the local network | 5 s |
| System-test | User flows, ie. simulating how a user would interact with the system |  no limitations. Is allowed to communicate with services outside the network | 30 s |

Currently we don't use e2e (though they do exists) tests, many of our integration test are very broad in scope and could count as system or end to end tests.

How we currently classify tests:

| Category | Scope | Limitations | Speed  |
|----------| :-------------:|:------:|----:|
| Unit | very small| only tests a single method |  100 ms|
| (Integration narrow) Unit | same scope as narrow integration test | Often only one dependency, and never the lora db | generally fast 50 - 200 ms|
| Integration | Generally a broader scope that tests how data flow though the api and to the db, and back again.  | Currently no real limitations  | 200 ms - 5000 ms, with a few being 30s or more|
| (System tests) Integration | A few broad test that gets data from other external services | no limitations |

\* Tests in parentheses indicates that the test is classified as one type but is actually another type.

### Test organization
! Currently this is not how the folder structure is organized.
The folder structure should be organized like this:

- os2mo/
	- backend/
		- tests/
			- conftest.py
			- unit/
			- integration/
				- conftest.py
				- graphql/
				- mora/
			- lora/
			- etc.

There exists a frontend test suite for Vue, however, its end-to-end part is unused at the current moment.

### Best practices

Test should be named test_testname (should not include whether they are integration and unit test in the filename).

#### Integration tests

Keep them narrow in scope.
Use fixtures to set state and data before and after tests.

## Pytest

### Conftest.py
We use pytest to run our tests. Pytest partitions each test into multiple stages.

- Collection phase (collects all the tests that should be run)
- Testcycle phase
	- Setup phase (runs before each test)
	- Call phase ( runs the test code)
	- Teardown phase ( runs after each test)
- Report phase (generates a report for each test)

How these phases are being conducted is determined by the conftest.py in each test folder. This file applies to the current and nested folders. This means that we can have a general conftest in `tests/` and one in `tests/integration/`, the results is the things we define in `tests/conftest.py` is applied to all tests, while the things defined in `tests/integration/` is only applied to integration tests.

### Fixtures

We use fixtures to define behavior and state for how each test should be run.

Commonly used fixtures:
| Fixture | Effect |
|----------|-------------|
| XXX_test_app |  A fixture that instantiates a mora fast api app. |
| load_fixture_data_with_reset | Ensures that the 'sample structures' has been loaded. And rollbacks all changes made during a test from the db. |
| graphapi_post | Allows the test to make a grapapi post request with a mocked client. |

Autoused fixture:
These fixtures are automatically loaded when running a test.

| Fixture | Effect |
|----------|-------------|
| mocked_context | Mocks the starlette context object to return an empty dict rather than an error, when failing |
| seed_lora_client | Creates an async lora client  |

### Marks
A test can be marked as being a certain type, most default marks dont do anything (They are generally used for test selection). However, the following marks do have actual effects on tests, as described below.

| Mark | Effect |
|----------|-------------|
| pytest.mark.integration_test | Marks the test as being an integration test, meaning that time limits apply to it. |

## Testclasses (Deprecated)

There are currently defined several `TestCase` classes that a test can use.
These are deprecated and we should not add any more of them, however they are still prominent in the codebase.

There exist two main Testclasses:

### Sync testclass

The basic testclasses use the `_BaseTestCase` and derivatives of this class.
When inhereting from this class a setup method will automatically be called and instantiate a mora fast api app, from which test can be run against.

It also adds the ability to call `assertRequest`-methods against said app.

### Async testclass
`_AsyncBaseTestCase` is like the sync testclasses but it works asynchronously by having a managed lifetime object.

when running the setup method of this class, a [lifespan](https://asgi.readthedocs.io/en/latest/specs/lifespan.html) manger will be added to the eventloop. This means that tests inheriting from this class will terminate the connection to the app when done running.

### Why deprecated?

TBD

## Hypothesis

we use two different settings for hypothesis, dev & ci.
dev runs 10 mutations and ci runs 30. Beware: this can lead to tests failing in pipeline and not locally.

https://hypothesis.readthedocs.io/en/latest/


## Test commands
### Integration tests

`docker-compose exec -u 0 mo pytest` -> run all test

`docker-compose exec -u 0 mo pytest backend/tests/testfile::TestClass::test_method` -> for running specific tests.

usefull args:
`--show-capture=stdout` omit all logging but stdout
`--disable-pytest-warnings` -> disable warnings
`-vv` -> very verbose
`-x` -> stop at first test
`-s` -> with print statements
`--splits <amount runners in ci>` `--group <integration test number>`
`` -> runs the same selection as a pipeline has.

Want to run a debugger inside the container on a failing test? See [link to container debugging](https://rammearkitektur.docs.magenta.dk/development/tips-tricks.html#debugging-in-a-docker-container)

### Unit tests
Note:  see [Local vs CI](### Local vs CI) for a guide to get unit test running locally without failing
```
# from os2mo/backend
poetry run pytest tests \
      -p no:cacheprovider \
      -m "not integration_test" \
      --show-capture=stdout \
      --cov=mora
```

## Local vs CI

### Unit tests
To get unit test to run the same way as they do in the pipeline, following environment variables must be set.

```
export ENVIRONMENT="testing";
export LORA_AUTH=false;
export DB_NAME=mox;
export AMQP_ENABLE=false;
export HYPOTHESIS_PROFILE=ci;
export DUMMY_MODE=true;
export QUERY_EXPORT_DIR=/tmp;
export FF_USE_FASTZIP=false;
export TESTING_API=true;
```

This means that currently only one test fails.

### Integration tests

Following config will produce the highest amount of correct tests:

In docker-compose.override.yml:

```
...
mox:
   environment:
    ENVIRONMENT: testing
    TESTING_API: "true"
    LORA_AUTH: "false"
    KEYCLOAK_SCHEMA: "http"
mo:
  environment:
    OS2MO_AUTH: "false"
    HYPOTHESIS_PROFILE: ci
```

However there are still following failing tests:

- backend/tests/test_lora.py
- backend/tests/test_integration_termination.py
- backend/tests/test_integration_validator.py
- backend/tests/test_service_auth.py
- backend/tests/oio_rest/test_sql.py

and the following test that simply times out:

- backend/tests/test_integration_it_system.py
- backend/tests/test_integration_org_unit.py
- backend/tests/shimmed/test_integration_org_unit.py

to avoid these test run:

`dce -u 0 mo pytest backend/tests -m "integration_test" -k "not test_integration_itsystem.py and not test_lora.py and not test_integration_termination.py and not test_service_auth.py and not test_sql.py and not test_integration_org_unit and not shimmed/test_organisation_unit.py"`

## More reading

https://martinfowler.com/bliki/IntegrationTest.html
https://docs.pytest.org/en/7.1.x/reference/reference.html

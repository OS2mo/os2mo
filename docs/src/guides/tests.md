---
title: Testsuite
---

## How to write tests

### Test categories

! *Not all tests currently adhere to this standard. However this should be the standard*

| Category | Scope | Limitations | Speed  |
|----------| :-------------:|:------:|----:|
| Unit | Assert that an action i completed correctly within a single module | No db, No network, no other system dependencies, should be able to be run without a container | very fast 50-100 ms|
| Integration - narrow | Test how a single module interacts with one other module | a max of one dependency (ie. a database OR a webserver ) | ~500 ms |
| Integration - broad | Asserts that an action behaves correctly thorugh multiple modules | Can use one machine, but not communicate with other services | 5000 ms |
| System-test | User flows, ie. simulating how a user would interact with the system |

Currently we dont use e2e tests, many of our integration test are very broad in scope and could count as system or end to end tests.

How we currently classify tests:
| Category | Scope | Limitations | Speed  |
|----------| :-------------:|:------:|----:|
| Unit | very small| only tests a single method |  <100 ms|
| ~~Unit~~ Integration  | same scope as narrow integration test | Often only one dependency, and never the lora db | generally fast ~50 - 200 ms|
| Integration | Generally a broader  | Currently no real limitations  | ~ 200 ms - 5000 ms, with a few being 30s or more|
| ~~System tests~~ Integration | A few broad test that gets data from other external services | no limations | |


### Test organization
! Currently this is not how the folder structure is organized.
The folder structure should be organized like this

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

There exists a frontend testsuite, however it's unused.


### Best practices

Test should be named test_testname (should not include whether they are integration and unit test in the filename)

#### Integration tests

Keep them narrow in scope.
Use fixtures to set state.

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

Commenly used fixtures:
| Fixture | Effect |
|----------| -------------|
| XXX_test_app |  A fixture that instantiates a mora fast api app. |
| load_fixture_data_with_reset | Ensures that the 'sample structures' has been loaded. And rollbacks all changes made during a test from the db. |
| graphapi_post | Allows the test to make a grapapi post request to the mocked  |

Autoused fixture:
These fixtures are automatically loaded when running a test.

| Fixture | Effect |
|----------| -------------|
| mocked_context |  |
| seed_lora_client | Creates an async lora client  |

### Marks
A test can be marked as being a certain type, most default marks dont do anything. However, the following marks do have actual effects on tests, as described below.


## Frontend unit tests


Frontend-koden har en række unit tests, der tester Vue-koden på
komponent-niveau. Disse findes i
`frontend/tests/unit/`{.interpreted-text role="file"}.

En stor del af kompleksiteten i frontend-koden består af koblingerne
mellem de forskellige Vue-komponenter. Disse koblinger bliver også
testet i form af Vue unit tests.

Efter at udviklingsmiljøet er startet med `docker-compose up -d`, kan
frontend unit tests køres med kommandoen:

``` {.bash}
docker-compose exec frontend yarn test:unit
```

Der kan produceres en HTML-rapport over [test coverage]{.title-ref} ved
at give flg. kommando:

``` {.bash}
docker-compose exec frontend yarn test:unit --coverage --coverageReporters=html
```

Coverage-rapporten kan så findes i
`frontend/coverage/index.html`{.interpreted-text role="file"}.

## Frontend end-to-end tests


Vores frontend har desuden end-to-end tests, der køres med værktøjet
[TestCafe](https://devexpress.github.io/testcafe/). Disse tests
simulerer museklik, tastetryk, osv. i en \"headless browser\", og
tjekker, at der sker de ønskede ændringer på skærmen, når de forskellige
sider og popup-vinduer aktiveres.

Vores end-to-end tests kan ikke køre parallelt med backend\'ens
integration tests, da de anvender samme LoRa-instans og samme database.
`testcafe`-servicen er derfor defineret i sin egen
`dev-environment/docker-compose-testcafe.yml`{.interpreted-text
role="file"} for at den ikke starter op, når man starter andre services
op.

Efter at udviklingsmiljøet er startet med `docker-compose up -d`, kan
TestCafe køres med kommandoen:

``` {.bash}
docker-compose -f dev-environment/docker-compose-testcafe.yml up
```

(Dette kald skriver en warning om at der er [orphan
containers]{.title-ref}. Det er forventeligt, og kan ignoreres. De
normale services defineret i `docker-compose.yml`{.interpreted-text
role="file"} er fra kaldet til
`docker-compose -f dev-environment/docker-compose-testcafe.yml` set som
[orphans]{.title-ref}.)

### Kør e2e tests lokalt


Ovenstående Docker-løsning er ikke særlig brugbar, hvis man skal skrive
nye tests eller debugge eksisterende tests.

I stedet kan man installere pakker til at køre e2e tests lokalt på sin
host maskine. (Forudsat man har NodeJS og Chrome installeret.)

``` {.bash}
cd frontend/e2e-tests
npm install
```

Derefter kan tests afvikles direkte i Chrome browser:

``` {.bash}
npm run test
```

### Husk korrekt konfiguration

Vær desuden opmærksom på, at end-to-end testene køres med den
MO-konfiguration, der er defineret i `tests.util.load_sample_confdb`. I
denne MO-konfiguration er alle \"feature flags\" slået til, således at
frontend-koden kører med et fuldt MO feature-sæt. Hvis du tilføjer flere
MO feature flags, er det derfor en god ide at tilføje navnet på dit
feature flag til `tests.util.load_sample_confdb`.

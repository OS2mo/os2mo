# GraphAPI Test Suite

This test suite aims to cover our GraphAPI implementation in `mora/graphpi` by using a mix of unit and integration tests.

## Mocks

During unit tests, it is important to mock away interfaces that are not specific to the tested functionality. This ensures that we do not test external interfaces and/or the same interfaces repeatedly, and that tests are relatively fast.

For example, if a data loader is unit tested, its data source should be mocked, and the loader should be called directly instead of implicitly through the schema/API. Then, we can test the data loader functionality and mock its returns when testing other functionality that relies on the data loader.

In integration tests, we only mock two things: LoRa (because it is an external interface) and the API server via a FastAPI test client. This ensures that integration tests can test behaviour from a query hits the API to the load of data.

## What to test

What and how to test code implemented in the GraphAPI depends on the type of functionality in question. Below, we list commonly occurring scenarios and the tests required.

### Queries

Implementation of queries usually consists of the following:

- One or more Strawberry types, optionally with resolvers.
- New data loaders, and/or updates to existing
- Updates to the schema in `mora/graphpi/main.py`

In this scenario, it is important to test data loaders in isolation as described previously. Then, queries can be executed against the schema to verify functionality of the implemented query with mocked data loaders.

It should always be tested that, given a known data source, queries return the expected output. Additionally, it should be tested that resolvers work as expected. These can be tested in isolation if they are defined outside the Strawberry type.

Care should be taken that we do not end up testing Strawberry functionality, but rather the business logic within our own code.

### API Context

If there are any changes to the context created within the API, it must _always_ be tested with a FastAPI client! In some cases, as with e.g. authentication, it can be necessary to mock the entire mora app (cf. `mora/app.py`). See `tests/graphapi/conftest.py` for an example of how to create a new test client.

## Hypothesis

Some tests within this suite makes use of Hypothesis, a property based testing library for Python. When writing tests using Hypothesis, it is **very** important to have a concise and simple property to test. Usually, it is beneficial to write many small unit tests first, and then see if some can be consolidated by testing properties with Hypothesis instead.

For example, our integration test in `test_graphapi` uses Hypothesis to generate all sorts of valid queries from the schema. We then state that, given a valid input, the API must always return status code 200 and no errors. Properties should not be much more complex than this, and if they are, seek immediate help - you risk getting lost in the test sauce.

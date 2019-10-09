import axios from 'axios';
import _ from 'lodash';

export let baseURL = process.env.BASE_URL || 'http://localhost:5000';

export function setup(ctx) {
  let request = axios.get(`${baseURL}/testing/testcafe-db-setup`);
  request
    .then(response => {
      if (_.isEqual(response.data, { 'testcafe-db-setup': true })) {

        ctx.setup_error = false;
        console.log("Setup database for testcafe.");

      } else {

        ctx.setup_error = true;
        console.error(
          "MOs testing API setup did not return the expected value. It returned: %s",
          response.data);
      }
    })
    .catch(error => {
      console.error("Call to MOs testing API setup failed: %s",
                    error.message);
      ctx.setup_error = true;
    });
};

export async function reset(test) {

  await test.expect(test.fixtureCtx.setup_error)
    .notOk("The database setup failed. Failing this test early.");

  let request = axios.get(`${baseURL}/testing/testcafe-db-reset`);
  request
    .then(response => {
      if (_.isEqual(response.data, { 'testcafe-db-reset': true })) {
        console.log("Resetting database for testcafe.");
      } else {
        console.error(
          "MOs testing API reset did not return the expected value. It returned: %s",
          response.data);
      }
    })
    .catch(error => {
      console.error("Call to MOs testing API reset failed: %s",
                    error.message);
    });
}

export function teardown(ctx) {

  if (ctx.setup_error) {
    console.warn("Setup of the test database failed. Skipping teardown.");
  } else {
    let request = axios.get(`${baseURL}/testing/testcafe-db-teardown`);

    request
      .then(response => {
        console.log("Teardown database for testcafe.");

        if (! (_.isEqual(response.data, { 'testcafe-db-teardown': true }))) {
          console.error(
            `MOs testing API teardown did not return the expected value.
The database may be left in an undesired state. The API returned: %s`,
            response.data);
        }
      })
      .catch(error => {
        console.error(
          `Call to MOs testing API teardown failed.
 The database may be left in an undesired state: %s`,
          error.message);
      });
  }
}

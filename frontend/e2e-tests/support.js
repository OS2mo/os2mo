// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import axios from "axios"
import _ from "lodash"

export let baseURL = process.env.BASE_URL || "http://localhost:5001"
export let bakendBaseURL = process.env.BASE_URL || "http://localhost:5000"

export async function setup(ctx) {
  await axios
    .get(`${bakendBaseURL}/testing/testcafe-db-setup`)
    .then((response) => {
      if (_.isEqual(response.data, { "testcafe-db-setup": true })) {
        ctx.setup_error = false
        console.log("Setup database for testcafe.")
      } else {
        ctx.setup_error = true
        console.error(
          "MOs testing API setup did not return the expected value. It returned: %s",
          response.data
        )
      }
    })
    .catch((error) => {
      console.error("Call to MOs testing API setup failed: %s", error.message)
      ctx.setup_error = true
    })
}

export async function teardown(ctx) {
  if (ctx.setup_error) {
    console.warn("Setup of the test database failed. Skipping teardown.")
  } else {
    await axios
      .get(`${bakendBaseURL}/testing/testcafe-db-teardown`)
      .then((response) => {
        console.log("Teardown database for testcafe.")

        if (!_.isEqual(response.data, { "testcafe-db-teardown": true })) {
          console.error(
            `MOs testing API teardown did not return the expected value.
The database may be left in an undesired state. The API returned: %s`,
            response.data
          )
        }
      })
      .catch((error) => {
        console.error(
          `Call to MOs testing API teardown failed.
 The database may be left in an undesired state: %s`,
          error.message
        )
      })
  }
}

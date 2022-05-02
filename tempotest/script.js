/*
 * SPDX-FileCopyrightText: 2022 Magenta ApS
 * SPDX-License-Identifier: MPL-2.0
 */
import apiGraphqlMetaTests from './tests/api.graphql.meta.js';
import apiServiceTests from './tests/api.service.js';
import apiServiceMetaTests from './tests/api.service.meta.js';
import { getAuthorizationHeader, client } from './util.js';

export const options = {
  // Discard response bodies by default to lessen the amount of memory required and the amount of
  // GC -- reducing the load on the testing machine, producing more reliable test results.
  discardResponseBodies: true,

  thresholds: {
    checks: ['rate==1.00'], // All checks must pass
    http_req_failed: ['rate==0.00'], // No requests may fail
    // GraphQL
    'http_req_duration{group:::api.graphql}': ['p(95) < 1'], // todo
    'http_req_duration{group:::api.graphql.list}': ['p(95) < 1'], // todo
    'http_req_duration{group:::api.graphql.meta}': ['p(95) < 150'],
    'http_req_duration{group:::api.graphql.meta.health}': ['p(95) < 250'],
    // Service API
    'http_req_duration{group:::api.service}': ['p(95) < 1'], // todo
    'http_req_duration{group:::api.service.list}': ['p(95) < 1'], // todo
    'http_req_duration{group:::api.service.meta}': ['p(95) < 150'],
    'http_req_duration{group:::api.service.meta.health}': ['p(95) < 300'],
  },
};

export function setup() {
  const authorizationHeader = getAuthorizationHeader();
  client.addHeader('Authorization', authorizationHeader);

  return {
    // set 'responseType' to override default 'discardResponseBodies = true', allowing us to
    // retrieve the json response
    orgUUID: client.get('/service/o/', null, { responseType: 'text' }).json('0.uuid'),
    authorizationHeader,
  };
}

export default function main(data) {
  // The authorization header cannot be configured in setup(), but needs to be set for each
  // iteration, as memory is not shared between the runners.
  // See https://k6.io/docs/using-k6/test-life-cycle/ for more information.
  client.addHeader('Authorization', data.authorizationHeader);

  apiServiceMetaTests();
  apiServiceTests();
  apiGraphqlMetaTests();
}

// export function teardown(data) {
//   // teardown code
// }

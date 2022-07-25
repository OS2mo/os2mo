/*
 * SPDX-FileCopyrightText: 2022 Magenta ApS
 * SPDX-License-Identifier: MPL-2.0
 */
import { Httpx } from 'https://jslib.k6.io/httpx/0.0.6/index.js';
import { check } from 'k6';
import exec from 'k6/execution';
import http from 'k6/http';

const MO_URL = __ENV.MO_URL || exec.test.abort('MO_URL not given.');
const CLIENT_ID = __ENV.CLIENT_ID || 'dipex';
const CLIENT_SECRET = __ENV.CLIENT_SECRET || exec.test.abort('CLIENT_SECRET not given.');
const AUTH_SERVER = __ENV.AUTH_SERVER || exec.test.abort('AUTH_SERVER not given.');
const AUTH_REALM = __ENV.AUTH_REALM || 'mo';

/**
 * Convert JSON payload to stringified representation with accompanying headers.
 * @param {array|object} data: JSON payload.
 * @param {object} extraParams: Extra parameters passed to the httpx request.
 * @returns {[string, object]}: Array containing the stringified body and accompanying headers.
 *
 * @example
 * client.post("/service/details/create", ...asJSON({
 *   uuid: uuid,
 * }))
 */
export function asJSON(data, extraParams) {
  const body = JSON.stringify(data);
  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  Object.assign(params, extraParams);
  return [body, params];
}

class Client extends Httpx {
  /**
   * Perform GraphQL query.
   * @param {string} query: GraphQL query. MUST be defined with a proper query name.
   * @param {string} url: Path to GraphQL endpoint.
   * @returns {object}: GraphQL query response.
   */
  graphql(query, url = '/graphql/latest') {
    const queryName = query.match(/\s*query (\w+)/)[1];
    const res = this.post(
      url,
      ...asJSON(
        {
          query,
        },
        {
          // set 'responseType' to override default 'discardResponseBodies = true', allowing us to
          // retrieve the json response to check for errors, as GraphQL always returns 200 OK.
          responseType: 'text',
          tags: {
            name: `graphql.${queryName}`,
          },
        },
      ),
    );
    check(res, {
      'Successful Response': (r) => !r.json('errors'),
    });
    return res;
  }
}

/** Global HTTPX client, imported and used by all tests. */
export const client = new Client({
  baseURL: MO_URL,
  timeout: 120000, // 2m timeout. May need to be increased to test the service api, lol
});

/**
 * Fetch and configure keycloak token header.
 * @param {string} clientId: Client identifier used to obtain token.
 * @param {string} clientSecret: Client secret used to obtain token.
 * @param {string} authServer: HTTP URL of the authentication server.
 * @param {string} authRealm: Keycloak realm used for authentication.
 * @returns {string}: Keycloak access token.
 */
export function getAuthorizationHeader(
  clientId = CLIENT_ID,
  clientSecret = CLIENT_SECRET,
  authServer = AUTH_SERVER,
  authRealm = AUTH_REALM,
) {
  const r = http.post(
    `${authServer}/realms/${authRealm}/protocol/openid-connect/token`,
    {
      grant_type: 'client_credentials',
      client_id: clientId,
      client_secret: clientSecret,
    },
    {
      responseType: 'binary', // override 'discardResponseBodies = true' default to get token data
    },
  );
  const data = r.json();
  if (data.expires_in < 1800) {
    console.warn('Token expiry less than 30 minutes:', data.expires_in, 'seconds.');
  }
  return `Bearer ${data.access_token}`;
}

/*
 * SPDX-FileCopyrightText: 2022 Magenta ApS
 * SPDX-License-Identifier: MPL-2.0
 */
import { group } from 'k6';
import { client } from '../util.js';

function version() {
  client.graphql(
    `
    query VersionQuery {
      version {
        lora_version
        mo_hash
        mo_version
      }
    }
    `,
  );
}

function healths() {
  client.graphql(
    `
    query HealthsQuery {
      healths {
        identifier
        status
      }
    }
    `,
  );
}

function org() {
  client.graphql(
    `
    query OrgQuery {
      org {
        uuid
        name
        user_key
        type
      }
    }
    `,
  );
}

export default function apiGraphqlMetaTests() {
  group('api.graphql.meta', () => {
    version();
    org();
  });
  group('api.graphql.meta.health', () => {
    healths();
  });
}

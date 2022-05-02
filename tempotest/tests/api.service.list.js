/*
 * SPDX-FileCopyrightText: 2022 Magenta ApS
 * SPDX-License-Identifier: MPL-2.0
 */
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';
import { group } from 'k6';
import http from 'k6/http';
import { asJSON, client } from '../util.js';

function engagement() {
  group('engagement', () => {
    const uuid = uuidv4();
    client.post(
      http.url`/service/details/create`,
      ...asJSON({
        uuid,
        todo,
      }),
    );
  });
}

function association() {
  group('association', () => {
    const uuid = uuidv4();
    client.post(
      http.url`/service/details/create`,
      ...asJSON({
        uuid,
        todo,
      }),
    );
  });
}

function itSystem() {
  group('itSystem', () => {
    const uuid = uuidv4();
    client.post(
      http.url`/service/details/create`,
      ...asJSON({
        uuid,
        todo,
      }),
    );
  });
}

function role() {
  group('role', () => {
    const uuid = uuidv4();
    client.post(
      http.url`/service/details/create`,
      ...asJSON({
        uuid,
        todo,
      }),
    );
  });
}

function manager() {
  group('manager', () => {
    const uuid = uuidv4();
    client.post(
      http.url`/service/details/create`,
      ...asJSON({
        uuid,
        todo,
      }),
    );
  });
}

function leave() {
  group('leave', () => {
    const uuid = uuidv4();
    client.post(
      http.url`/service/details/create`,
      ...asJSON({
        uuid,
        todo,
      }),
    );
  });
}

function address() {
  group('address', () => {
    const uuid = uuidv4();
    client.post(
      http.url`/service/details/create`,
      ...asJSON({
        uuid,
        todo,
      }),
    );
  });
}

function employee() {
  group('employee', () => {
    const uuid = uuidv4();
    client.post(
      http.url`/service/e/create`,
      ...asJSON({
        uuid,
        givenname: 'Alice',
      }),
    );
    client.get(http.url`/service/e/${uuid}/`);
  });
}

export default function apiServiceListTests() {
  group('api.service.list', () => {
    employee();
  });
}

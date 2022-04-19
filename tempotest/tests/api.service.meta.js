/*
 * SPDX-FileCopyrightText: 2022 Magenta ApS
 * SPDX-License-Identifier: MPL-2.0
 */
import { group } from 'k6';
import http from 'k6/http';
import { client } from '../util.js';

function version() {
  client.get(http.url`/version/`);
}

function health() {
  client.get(http.url`/health/`);
}

function live() {
  client.get(http.url`/health/live`);
}

function org() {
  client.get(http.url`/service/o/`);
}

export default function apiServiceMetaTests() {
  group('api.service.meta', () => {
    version();
    live();
    org();
  });
  group('api.service.meta.health', () => {
    health();
  });
}

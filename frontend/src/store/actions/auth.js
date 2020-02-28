// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import removeNamespace from '@/helpers/namespaceHelper'

const NAMESPACE = 'auth'

export const Auth = {
  NAMESPACE: NAMESPACE,
  actions: {
    AUTH_LOGOUT: `${NAMESPACE}/AUTH_LOGOUT`,
    AUTH_REQUEST: `${NAMESPACE}/AUTH_REQUEST`
  },
  mutations: {
    AUTH_LOGOUT: `${NAMESPACE}/AUTH_LOGOUT`,
    AUTH_SUCCESS: `${NAMESPACE}/AUTH_SUCCESS`,
    AUTH_ERROR: `${NAMESPACE}/AUTH_ERROR`
  },
  getters: {
    GET_USERNAME: `${NAMESPACE}/GET_USERNAME`,
    GET_STATUS: `${NAMESPACE}/GET_STATUS`,
    GET_ACCESS_TOKEN: `${NAMESPACE}/GET_ACCESS_TOKEN`,
    IS_AUTHENTICATED: `${NAMESPACE}/IS_AUTHENTICATED`
  }
}

export const _auth = removeNamespace(`${NAMESPACE}/`, Auth)

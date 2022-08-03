// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import removeNamespace from "@/helpers/namespaceHelper"

const NAMESPACE = "organisation"

export const Organisation = {
  NAMESPACE: NAMESPACE,
  actions: {
    SET_ORGANISATION: `${NAMESPACE}/SET_ORGANISATION`,
  },
  mutations: {
    SET_ORGANISATION: `${NAMESPACE}/SET_ORGANISATION`,
  },
  getters: {
    GET_ORGANISATION: `${NAMESPACE}/GET_ORGANISATION`,
    GET_UUID: `${NAMESPACE}/GET_UUID`,
  },
}

export const _organisation = removeNamespace(`${NAMESPACE}/`, Organisation)

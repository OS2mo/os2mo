// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import removeNamespace from "@/helpers/namespaceHelper"

const NAMESPACE = "facet"

export const Facet = {
  NAMESPACE: NAMESPACE,
  actions: {
    SET_FACET: `${NAMESPACE}/SET_FACET`,
  },
  mutations: {
    SET_FACET: `${NAMESPACE}/SET_FACET`,
  },
  getters: {
    GET_FACET: `${NAMESPACE}/GET_FACET`,
    GET_UUID: `${NAMESPACE}/GET_UUID`,
  },
}

export const _facet = removeNamespace(`${NAMESPACE}/`, Facet)

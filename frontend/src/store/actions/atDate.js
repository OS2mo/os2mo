// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import removeNamespace from "@/helpers/namespaceHelper"

const NAMESPACE = "atDate"

export const AtDate = {
  NAMESPACE: NAMESPACE,
  actions: {
    SET: `${NAMESPACE}/SET`,
  },
  mutations: {
    SET: `${NAMESPACE}/SET`,
  },
  getters: {
    GET: `${NAMESPACE}/GET`,
  },
}

export const _atDate = removeNamespace(`${NAMESPACE}/`, AtDate)

// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import removeNamespace from "@/helpers/namespaceHelper"

const NAMESPACE = "engagement"

export const Engagement = {
  NAMESPACE: NAMESPACE,
  actions: {
    SET_ENGAGEMENT: `${NAMESPACE}/SET_ENGAGEMENT`,
    SET_DETAIL: `${NAMESPACE}/SET_DETAIL`,
  },
  mutations: {
    SET_ENGAGEMENT: `${NAMESPACE}/SET_ENGAGEMENT`,
    SET_DETAIL: `${NAMESPACE}/SET_DETAIL`,
    RESET_ENGAGEMENT: `${NAMESPACE}/RESET_ENGAGEMENT`,
  },
  getters: {
    GET_ENGAGEMENT: `${NAMESPACE}/GET_ENGAGEMENT`,
    GET_DETAIL: `${NAMESPACE}/GET_DETAIL`,
    GET_DETAILS: `${NAMESPACE}/GET_DETAILS`,
  },
}

export const _engagement = removeNamespace(`${NAMESPACE}/`, Engagement)

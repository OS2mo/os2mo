// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import removeNamespace from "@/helpers/namespaceHelper"

const NAMESPACE = "employee"

export const Employee = {
  NAMESPACE: NAMESPACE,
  actions: {
    SET_EMPLOYEE: `${NAMESPACE}/SET_EMPLOYEE`,
    SET_DETAIL: `${NAMESPACE}/SET_DETAIL`,
  },
  mutations: {
    SET_EMPLOYEE: `${NAMESPACE}/SET_EMPLOYEE`,
    SET_DETAIL: `${NAMESPACE}/SET_DETAIL`,
    RESET_EMPLOYEE: `${NAMESPACE}/RESET_EMPLOYEE`,
  },
  getters: {
    GET_EMPLOYEE: `${NAMESPACE}/GET_EMPLOYEE`,
    GET_DETAIL: `${NAMESPACE}/GET_DETAIL`,
    GET_DETAILS: `${NAMESPACE}/GET_DETAILS`,
  },
}

export const _employee = removeNamespace(`${NAMESPACE}/`, Employee)

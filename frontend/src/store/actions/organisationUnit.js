// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import removeNamespace from "@/helpers/namespaceHelper"

const NAMESPACE = "organisationUnit"

export const OrganisationUnit = {
  NAMESPACE: NAMESPACE,
  actions: {
    SET_ORG_UNIT: `${NAMESPACE}/SET_ORG_UNIT`,
    SET_DETAIL: `${NAMESPACE}/SET_DETAIL`,
  },
  mutations: {
    SET_ORG_UNIT: `${NAMESPACE}/SET_ORG_UNIT`,
    SET_DETAIL: `${NAMESPACE}/SET_DETAIL`,
    RESET_ORG_UNIT: `${NAMESPACE}/RESET_ORG_UNIT`,
  },
  getters: {
    GET_ORG_UNIT: `${NAMESPACE}/GET_ORG_UNIT`,
    GET_ORG_UNIT_UUID: `${NAMESPACE}/GET_ORG_UNIT_UUID`,
    GET_DETAIL: `${NAMESPACE}/GET_DETAIL`,
    GET_DETAILS: `${NAMESPACE}/GET_DETAILS`,
  },
}

export const _organisationUnit = removeNamespace(`${NAMESPACE}/`, OrganisationUnit)

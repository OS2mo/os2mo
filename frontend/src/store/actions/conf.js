// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import removeNamespace from "@/helpers/namespaceHelper"

const NAMESPACE = "conf"

export const Conf = {
  NAMESPACE: NAMESPACE,
  actions: {
    SET_CONF_DB: `${NAMESPACE}/SET_CONF_DB`,
    SET_NAVLINKS: `${NAMESPACE}/SET_NAVLINKS`,
  },
  mutations: {
    SET_CONF_DB: `${NAMESPACE}/SET_CONF_DB`,
    SET_NAVLINKS: `${NAMESPACE}/SET_NAVLINKS`,
  },
  getters: {
    GET_CONF_DB: `${NAMESPACE}/GET_CONF_DB`,
    GET_NAVLINKS: `${NAMESPACE}/GET_NAVLINKS`,
  },
}

export const _conf = removeNamespace(`${NAMESPACE}/`, Conf)

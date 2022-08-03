// SPDX-FileCopyrightText: 2019-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "@/api/HttpCommon"
import { _conf } from "../actions/conf"

const state = {
  conf: {},
  navlinks: {},
}

const actions = {
  [_conf.actions.SET_CONF_DB]: ({ commit }) => {
    return Service.get(`/configuration`)
      .then((response) => {
        commit(_conf.mutations.SET_CONF_DB, response.data)
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },
  [_conf.actions.SET_NAVLINKS]: ({ commit }) => {
    return Service.get(`/navlinks`)
      .then((response) => {
        let nonEmptyNavLinks = response.data.filter(
          (navlink) => navlink && navlink.href !== undefined
        )
        commit(_conf.mutations.SET_NAVLINKS, nonEmptyNavLinks)
      })
      .catch((error) => {
        commit("log/newError", { type: "ERROR", value: error.response }, { root: true })
      })
  },
}

const mutations = {
  [_conf.mutations.SET_CONF_DB](state, payload) {
    state.conf = payload
  },
  [_conf.mutations.SET_NAVLINKS](state, payload) {
    state.navlinks = payload
  },
}

const getters = {
  [_conf.getters.GET_CONF_DB]: (state) => state.conf,
  [_conf.getters.GET_NAVLINKS]: (state) => state.navlinks,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}

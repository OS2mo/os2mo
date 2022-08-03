// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import { _atDate } from "../actions/atDate"

const state = {
  value: new Date(),
}

const actions = {
  [_atDate.actions.SET]({ state, rootState, commit }, value) {
    commit("SET", value)
  },
}

const mutations = {
  [_atDate.mutations.SET](state, data) {
    state.value = data
  },
}

const getters = {
  [_atDate.getters.GET]: (state) => state.value,
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
}

// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

import Service from "@/api/HttpCommon"

const state = {
  queries: [],
}

const actions = {
  getQueries: ({ commit }) => {
    Service.get("/exports/").then((response) => {
      commit("setQueries", response.data)
    })
  },
}

const mutations = {
  setQueries(store, payload) {
    store.queries = payload
  },
}

const getters = {
  getQueries: (state) => state.queries,
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters,
}

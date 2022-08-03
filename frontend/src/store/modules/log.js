// SPDX-FileCopyrightText: 2018-2020 Magenta ApS
// SPDX-License-Identifier: MPL-2.0

const state = {
  workLog: [],
  errors: [],
}

const mutations = {
  newWorkLog(state, value) {
    state.workLog.push(value)
  },
  newError(state, log) {
    state.errors.push(log)
  },
}

const getters = {
  getWorkLog: (state) => state.workLog,
  getErrors: (state) => state.errors,
}

export default {
  namespaced: true,
  state,
  mutations,
  getters,
}

const state = {
  workLog: [],
  errors: []
}

const mutations = {
  newWorkLog (state, value) {
    state.workLog.push(value)
  },
  newError (state, log) {
    state.errors.push(log)
  }
}

const getters = {
  getWorkLog: state => state.workLog,
  getErrors: state => state.errors
}

export default {
  namespaced: true,
  state,
  mutations,
  getters
}

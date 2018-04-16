const state = {
  workLog: [],
  events: [],
  errors: []
}

const mutations = {
  newWorkLog (state, value) {
    state.workLog.push(value)
  },
  newEvent (state, log) {
    state.events.push(log)
  },
  newError (state, log) {
    state.errors.push(log)
  }
}

const getters = {
  getWorkLog: state => state.workLog,
  getEvents: state => state.events,
  getErrors: state => state.errors
}

export default {
  namespaced: true,
  state,
  // actions,
  mutations,
  getters
}

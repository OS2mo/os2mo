const state = {
  from: {
    org: undefined,
    orgUnit: undefined
  },
  to: {

  },
  name: undefined,
  uuid: undefined
}

const actions = {

}

const mutations = {
  change (state, employee) {
    state.name = employee.name
    state.uuid = employee.uuid
  }
}

const getters = {
  getUuid: state => state.uuid,
  get: state => state
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

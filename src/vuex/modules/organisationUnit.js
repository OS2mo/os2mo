const state = {
  name: undefined,
  user_key: undefined,
  uuid: undefined
}

const mutations = {
  change (state, orgUnit) {
    state.name = orgUnit.name
    state.user_key = orgUnit.user_key
    state.uuid = orgUnit.uuid
  },

  reset (state) {
    state.name = undefined
    state.user_key = undefined
    state.uuid = undefined
  }
}

const getters = {
  getOrgUnit: state => state
}

export default {
  namespaced: true,
  state,
  // actions,
  mutations,
  getters
}

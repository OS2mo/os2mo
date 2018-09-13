const state = {
  name: undefined,
  user_key: undefined,
  uuid: undefined,
  user_settings: {}
}

const mutations = {
  change (state, dataObject) {
    state.name = dataObject.name
    state.user_key = dataObject.user_key
    state.uuid = dataObject.uuid
    state.user_settings = dataObject.user_settings
  },

  reset (state) {
    state.name = undefined
    state.user_key = undefined
    state.uuid = undefined
    state.user_settings = {}
  }
}

const getters = {
  getOrgUnit (state) {
    return state
  },
  getOrgUnitSettings (state) {
    return state.user_settings.orgunit
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  getters
}

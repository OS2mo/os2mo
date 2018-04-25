const state = {
  name: undefined,
  user_key: undefined,
  uuid: undefined
}

const mutations = {
  change (state, organisation) {
    state.name = organisation.name
    state.user_key = organisation.user_key
    state.uuid = organisation.uuid
  }
}

const getters = {
  getUuid: state => state.uuid,
  get: state => state
}

export default {
  namespaced: true,
  state,
  // actions,
  mutations,
  getters
}

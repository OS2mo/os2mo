import Service from '@/api/HttpCommon'

const state = {
  name: undefined,
  user_key: undefined,
  uuid: undefined
}

const actions = {
  setOrg ({ commit, rootState }, payload) {
    console.log(payload)
    return Service.get(`/o/${payload}/`)
      .then(response => {
        commit('setOrg', response.data)
      })
      .catch(error => {
        rootState.commit('log/newError', { type: 'ERROR', value: error.response })
      })
  }
}

const mutations = {
  setOrg (state, payload) {
    state.name = payload.name
    state.user_key = payload.user_key
    state.uuid = payload.uuid
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

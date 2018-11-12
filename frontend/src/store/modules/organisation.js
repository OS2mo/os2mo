import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  name: undefined,
  user_key: undefined,
  uuid: undefined
}

const actions = {
  setOrg ({ commit }, payload) {
    console.log(payload)
    return Service.get(`/o/${payload}/`)
      .then(response => {
        commit('setOrg', response.data)
        EventBus.$emit('organisation-changed', response.data)
      })
      .catch(error => {
        commit('log/newError', { type: 'ERROR', value: error.response }, { root: true })
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

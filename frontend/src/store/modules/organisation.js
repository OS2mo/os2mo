import Service from '@/api/HttpCommon'
import { EventBus, Events } from '@/EventBus'
import { _organisation } from '../actions/organisation'

const state = {
  name: undefined,
  user_key: undefined,
  uuid: undefined
}

const actions = {
  [_organisation.actions.SET_ORGANISATION] ({ commit }, payload) {
    return Service.get(`/o/${payload}/`)
      .then(response => {
        commit(_organisation.mutations.SET_ORGANISATION, response.data)
        EventBus.$emit(Events.ORGANISATION_CHANGED, response.data)
      })
      .catch(error => {
        commit('log/newError', { type: 'ERROR', value: error.response }, { root: true })
      })
  }
}

const mutations = {
  [_organisation.mutations.SET_ORGANISATION] (state, payload) {
    state.name = payload.name
    state.user_key = payload.user_key
    state.uuid = payload.uuid
  }
}

const getters = {
  [_organisation.getters.GET_UUID]: state => state.uuid,
  [_organisation.getters.GET_ORGANISATION]: state => state
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

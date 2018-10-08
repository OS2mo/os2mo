import Service from '@/api/HttpCommon'
import { GET_ORG_UNIT, SET_ORG_UNIT, RESET_ORG_UNIT } from '../actions/organisationUnit'
const state = {
  name: undefined,
  user_key: undefined,
  uuid: undefined,
  org_uuid: undefined,
  parent_uuid: undefined
}

const actions = {
  [SET_ORG_UNIT] ({ rootState, commit }, payload) {
    return Service.get(`/ou/${payload}/`)
      .then(response => {
        commit(SET_ORG_UNIT, response.data)
        // EventBus.$emit('organisation-changed', response.data.org)
      })
      .catch(error => {
        rootState.commit('log/newError', { type: 'ERROR', value: error.response })
      })
  }
}

const mutations = {
  [SET_ORG_UNIT] (state, payload) {
    state.name = payload.name
    state.user_key = payload.user_key
    state.uuid = payload.uuid
    state.org_uuid = payload.org.uuid
    state.parent_uuid = payload.parent.uuid
  },

  [RESET_ORG_UNIT] (state) {
    state.name = undefined
    state.user_key = undefined
    state.uuid = undefined
    state.org_uuid = undefined
    state.parent_uuid = undefined
  }
}

const getters = {
  [GET_ORG_UNIT]: state => state
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

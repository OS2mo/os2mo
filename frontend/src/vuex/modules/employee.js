import { GET_EMPLOYEE, SET_EMPLOYEE, RESET_EMPLOYEE, SET_DETAIL, GET_DETAIL } from '../actions/employee'
import Service from '@/api/HttpCommon'

const state = {
  cpr_no: '',
  name: '',
  user_key: '',
  uuid: ''
}

const actions = {
  [SET_EMPLOYEE] ({ rootState, commit }, payload) {
    return Service.get(`/e/${payload}/`)
      .then(response => {
        commit(SET_EMPLOYEE, response.data)
        // EventBus.$emit('organisation-changed', response.data.org)
        return response.data
      })
      .catch(error => {
        rootState.commit('log/newError', { type: 'ERROR', value: error.response })
      })
  },

  [SET_DETAIL] ({ state, rootState, commit }, payload) {
    payload.validity = payload.validity || 'present'
    return Service.get(`/e/${state.uuid}/details/${payload.detail}?validity=${payload.validity}`)
      .then(response => {
        console.log('hello')
        // return response.data
      })
      .catch(error => {
        rootState.commit('log/newError', { type: 'ERROR', value: error.response })
      })
  }
}

const mutations = {
  [SET_EMPLOYEE] (state, payload) {
    state.cpr_no = payload.cpr_no
    state.name = payload.name
    state.user_key = payload.user_key
    state.uuid = payload.uuid
  },

  [RESET_EMPLOYEE] (state) {
    state.cpr_no = undefined
    state.name = undefined
    state.user_key = undefined
    state.uuid = undefined
  },

  [SET_DETAIL] (state, payload) {
    // TODO
  }
}

const getters = {
  [GET_EMPLOYEE]: state => state,
  [GET_DETAIL]: (state) => (id) => state[id] || {}
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

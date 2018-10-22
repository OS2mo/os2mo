import Vue from 'vue'
import Service from '@/api/HttpCommon'

const state = {
  cpr_no: undefined,
  name: undefined,
  user_key: undefined,
  uuid: undefined,
  details: {}
}

const actions = {
  SET_EMPLOYEE ({ commit }, payload) {
    return Service.get(`/e/${payload}/`)
      .then(response => {
        commit('SET_EMPLOYEE', response.data)
        // EventBus.$emit('organisation-changed', response.data.org)
        return response.data
      })
      .catch(error => {
        commit('log/newError', { type: 'ERROR', value: error.response }, { root: true })
      })
  },

  SET_DETAIL ({ state, commit }, payload) {
    payload.validity = payload.validity || 'present'
    let uuid = payload.uuid || state.uuid
    return Service.get(`/e/${uuid}/details/${payload.detail}?validity=${payload.validity}`)
      .then(response => {
        let content = {
          key: payload.detail,
          validity: payload.validity,
          value: response.data
        }
        commit('SET_DETAIL', content)
      })
      .catch(error => {
        commit('log/newError', { type: 'ERROR', value: error.response }, { root: true })
      })
  }
}

const mutations = {
  SET_EMPLOYEE (state, payload) {
    state.cpr_no = payload.cpr_no
    state.name = payload.name
    state.user_key = payload.user_key
    state.uuid = payload.uuid
  },

  RESET_EMPLOYEE (state) {
    state.cpr_no = undefined
    state.name = undefined
    state.user_key = undefined
    state.uuid = undefined
    state.details = {}
  },

  SET_DETAIL (state, payload) {
    if (!state.details[payload.key]) {
      Vue.set(state.details, payload.key, {})
    }
    Vue.set(state.details[payload.key], payload.validity, payload.value)
  }
}

const getters = {
  GET_EMPLOYEE: state => state,
  GET_DETAIL: (state) => (id) => state.details[id] || {},
  GET_DETAILS: (state) => state.details || {}
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

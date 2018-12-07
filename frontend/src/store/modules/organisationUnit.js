import Vue from 'vue'
import router from '@/router'
import Service from '@/api/HttpCommon'

const defaultState = () => {
  return {
    name: undefined,
    user_key: undefined,
    uuid: undefined,
    org: undefined,
    org_uuid: undefined,
    parent_uuid: undefined,
    parents: [],
    location: undefined,
    user_settings: {},
    details: {},
    isLoading: false
  }
}

const state = defaultState()

const actions = {
  async SET_ORG_UNIT ({ commit }, payload) {
    const response = await Service.get(`/ou/${payload}/`)

    if (response) {
      router.push({ name: 'OrganisationDetail', params: { uuid: response.data.uuid } })
      commit('SET_ORG_UNIT', response.data)
    } else {
      commit('log/newError', { type: 'ERROR', value: response }, { root: true })
    }
    return response.data
  },

  SET_DETAIL ({ state, commit }, payload) {
    payload.validity = payload.validity || 'present'
    let uuid = payload.uuid || state.uuid
    let atDate = payload.atDate || new Date()
    if (atDate instanceof Date) atDate = atDate.toISOString().split('T')[0]
    return Service.get(`/ou/${uuid}/details/${payload.detail}?validity=${payload.validity}&at=${atDate}`)
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
  SET_ORG_UNIT (state, payload) {
    state.uuid = payload.uuid
    state.name = payload.name
    state.uuid = payload.uuid
    state.user_key = payload.user_key
    state.org = payload.org
    state.org_uuid = payload.org.uuid
    state.location = payload.location
    state.user_settings = payload.user_settings
    state.parent_uuid = payload.parent.uuid
    state.parents = []

    for (let current = payload.parent; current; current = current.parent) {
      state.parents.push(current.uuid)
    }
  },

  RESET_ORG_UNIT (state) {
    Object.assign(state, defaultState())
  },

  SET_DETAIL (state, payload) {
    if (!state.details[payload.key]) {
      Vue.set(state.details, payload.key, {})
    }
    Vue.set(state.details[payload.key], payload.validity, payload.value)
  }
}

const getters = {
  GET_ORG_UNIT: state => state,
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

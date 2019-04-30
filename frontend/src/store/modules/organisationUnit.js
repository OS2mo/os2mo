import Vue from 'vue'
import Service from '@/api/HttpCommon'
import { _organisationUnit as _orgUnit } from '../actions/organisationUnit'

const defaultState = () => {
  return {
    name: undefined,
    user_key: undefined,
    uuid: undefined,
    org: undefined,
    org_uuid: undefined,
    parents: [],
    location: undefined,
    user_settings: {},
    details: {},
    isLoading: false
  }
}

const state = defaultState

const actions = {
  async [_orgUnit.actions.SET_ORG_UNIT] ({ commit }, payload) {
    const response = await Service.get(`/ou/${payload}/`)

    if (response) {
      commit(_orgUnit.mutations.SET_ORG_UNIT, response.data)
    } else {
      commit('log/newError', { type: 'ERROR', value: response }, { root: true })
    }
    return response.data
  },

  [_orgUnit.actions.SET_DETAIL] ({ state, commit }, payload) {
    payload.validity = payload.validity || 'present'
    let uuid = payload.uuid || state.uuid
    let atDate = payload.atDate || new Date()
    let inherit_manager_flag = ""
    if (atDate instanceof Date) atDate = atDate.toISOString().split('T')[0]
    if (payload.detail === "manager") inherit_manager_flag = "&inherit_manager=1"
    return Service.get(`/ou/${uuid}/details/${payload.detail}?validity=${payload.validity}&at=${atDate}${inherit_manager_flag}`)
      .then(response => {
        let content = {
          key: payload.detail,
          validity: payload.validity,
          value: response.data
        }
        commit(_orgUnit.mutations.SET_DETAIL, content)
      })
      .catch(error => {
        commit('log/newError', { type: 'ERROR', value: error.response }, { root: true })
      })
  }
}

const mutations = {
  [_orgUnit.mutations.SET_ORG_UNIT] (state, payload) {
    state.uuid = payload.uuid
    state.name = payload.name
    state.user_key = payload.user_key
    state.org = payload.org
    state.org_uuid = payload.org.uuid
    state.location = payload.location
    state.user_settings = payload.user_settings
    state.parents = []

    for (let current = payload.parent; current; current = current.parent) {
      state.parents.push(current.uuid)
    }
  },

  [_orgUnit.mutations.RESET_ORG_UNIT] (state) {
    Object.assign(state, defaultState())
  },

  [_orgUnit.mutations.SET_DETAIL] (state, payload) {
    if (!state.details[payload.key]) {
      Vue.set(state.details, payload.key, {})
    }
    Vue.set(state.details[payload.key], payload.validity, payload.value)
  }
}

const getters = {
  [_orgUnit.getters.GET_ORG_UNIT]: state => state,
  [_orgUnit.getters.GET_ORG_UNIT_UUID]: state => state.uuid,
  [_orgUnit.getters.GET_DETAIL]: (state) => (id) => state.details[id] || {},
  [_orgUnit.getters.GET_DETAILS]: (state) => state.details || {}
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

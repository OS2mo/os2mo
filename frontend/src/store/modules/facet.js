import Vue from 'vue'
import Service from '@/api/HttpCommon'

const state = {
  org_unit_address_type: undefined,
  employee_address_type: undefined,
  manager_address_type: undefined,
  association_type: undefined,
  engagement_type: undefined,
  engagement_job_function: undefined,
  association_job_function: undefined,
  leave_type: undefined,
  manager_level: undefined,
  manager_type: undefined,
  org_unit_type: undefined,
  responsibility: undefined,
  role_type: undefined
}

const actions = {
  SET_FACET ({ state, rootState, commit }, payload) {
    if (state[payload.facet]) return
    return Service.get(`/o/${rootState.organisation.uuid}/f/${payload}/`)
      .then(response => {
        response.data.classes = response.data.data.items
        delete response.data.data.items
        commit('SET_FACET', response.data)
      })
      .catch(error => {
        commit('log/newError', { type: 'ERROR', value: error.response }, { root: true })
      })
  }
}

const mutations = {
  SET_FACET (state, payload) {
    Vue.set(state, payload.user_key, payload)
  }
}

const getters = {
  GET_FACET: (state) => (id) => state[id] || {}
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

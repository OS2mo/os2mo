import { SET_FACET, GET_FACET } from '../actions/facet'
import Service from '@/api/HttpCommon'

const state = {
  address_type: undefined,
  association_type: undefined,
  engagement_type: undefined,
  job_function: undefined,
  leave_type: undefined,
  manager_level: undefined,
  manager_type: undefined,
  org_unit_type: undefined,
  responsibility: undefined,
  role_type: undefined
}

const actions = {
  [SET_FACET] ({ state, rootState, commit }, payload) {
    if (state[payload.facet]) return
    return Service.get(`/o/${rootState.organisation.uuid}/f/${payload}/`)
      .then(response => {
        commit(SET_FACET, response.data)
      })
      .catch(error => {
        console.log(error)
      })
  }
}

const mutations = {
  [SET_FACET] (state, payload) {
    payload.data.items = payload.data.items.slice().sort((a, b) => {
      if (a.name < b.name) return -1
      if (a.name > b.name) return 1
      return 0
    })
    state[payload.name] = payload
  }
}

const getters = {
  [GET_FACET]: (state) => (id) => (state[id] === undefined) ? { data: {} } : state[id]
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

import { getField, updateField } from 'vuex-map-fields'
import Service from '@/api/HttpCommon'
import OrganisationUnit from '@/api/OrganisationUnit'
import { EventBus } from '@/EventBus'

const state = {
  employees: [],
  selected: [],
  moveDate: null,
  orgUnitSource: null,
  orgUnitDestination: null,
  backendValidationError: null,
  isLoading: false,
  columns: [
    { label: 'person', data: 'person' },
    { label: 'engagement_type', data: 'engagement_type' },
    { label: 'job_function', data: 'job_function' }
  ]
}

const actions = {
  moveManyEmployees ({ commit }) {
    let moves = state.selected.map(engagement => {
      return {
        type: 'engagement',
        uuid: engagement.uuid,
        data: {
          org_unit: state.orgUnitDestination,
          validity: {
            from: state.moveDate
          }
        }
      }
    })

    commit('updateIsLoading', true)

    return Service.post('/details/edit', moves)
      .then(response => {
        EventBus.$emit('employee-changed')
        commit('updateIsLoading', false)
        commit('log/newWorkLog', { type: 'EMPLOYEE_MOVE', value: response.data }, { root: true })
        return response
      })
      .catch(error => {
        commit('updateError', error.response.data)
        commit('updateIsLoading', false)
        commit('log/newError', { type: 'ERROR', value: error.response.data }, { root: true })
        return error
      })
  },

  getEmployees ({ state, commit }) {
    if (!state.orgUnitSource) return
    OrganisationUnit.getDetail(state.orgUnitSource.uuid, 'engagement')
      .then(response => {
        commit('updateEmployees', response)
      })
      .catch(error => {
        commit('log/newError', { type: 'ERROR', value: error.response.data }, { root: true })
      })
  },

  resetFields ({ commit }) {
    commit('resetFields')
  }
}

const mutations = {
  updateField,

  updateError (state, error) {
    state.backendValidationError = error
  },

  updateIsLoading (state, isLoading) {
    state.isLoading = isLoading
  },

  updateOrgUnitSource (state, orgUnit) {
    state.orgUnitSource = orgUnit
  },

  updateEmployees (state, employees) {
    state.employees = employees
  },

  resetFields (state) {
    state.employees = []
    state.selected = []
    state.moveDate = null
    state.orgUnitSource = null
    state.orgUnitDestination = null
    state.backendValidationError = null
    state.isLoading = false
  }
}

const getters = {
  getField,

  employees: state => state.employees
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

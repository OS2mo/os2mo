import { getField, updateField } from 'vuex-map-fields'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  employees: [],
  selected: [],
  moveDate: null,
  orgUnitSource: null,
  orgUnitDestination: null,
  backendValidationError: null,
  columns: [
    {label: 'person', data: 'person'},
    {label: 'engagement_type', data: 'engagement_type'},
    {label: 'job_function', data: 'job_function'}
  ]
}

const actions = {
  MOVE_MANY_EMPLOYEES ({commit}) {
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
    return Service.post('/details/edit', moves)
    .then(response => {
      EventBus.$emit('employee-changed')
      commit('log/newWorkLog', { type: 'EMPLOYEE_MOVE', value: response })
      return response.data
    })
    .catch(error => {
      commit('log/newError', { type: 'ERROR', value: error.response.data })
      return error.response.data
    })
  },

  resetFields ({ commit }) {
    commit('resetFields')
  }
}

const mutations = {
  updateField,

  resetFields (state) {
    state.employees = []
    state.selected = []
    state.moveDate = null
    state.orgUnitSource = null
    state.orgUnitDestination = null
    state.backendValidationError = null
  }
}

const getters = {
  getField
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

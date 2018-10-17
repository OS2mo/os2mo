import { MOVE_EMPLOYEE, SET_EMPLOYEE, GET_EMPLOYEE, SET_ORG, GET_ORG, GET_VALIDITY, SET_VALIDITY } from '../actions/employeeMove'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  person: {},
  type: 'engagement',
  validity: {
    from: ''
  },
  org_unit: {}
}

const actions = {
  [MOVE_EMPLOYEE] ({commit, state}, payload) {
    return Service.post('/details/edit', [state])
    .then(response => {
      EventBus.$emit('employee-changed')
      this.commit('log/newWorkLog', { type: 'EMPLOYEE_MOVE', value: response })
      return response.data
    })
    .catch(error => {
      this.commit('log/newError', { type: 'ERROR', value: error.response.data })
      return error.response.data
    })
  }
}

const mutations = {
  change (state, employee) {
    state.person = employee.person
    state.validity.from = employee.validity.from
    state.org_unit = employee.org_unit
  },
  [SET_EMPLOYEE] (state, payload) {
    state.person = payload
  },
  [SET_ORG] (state, payload) {
    state.org_unit = payload
  },
  [SET_VALIDITY] (state, payload) {
    state.validity.from = payload
  }
}

const getters = {
  [GET_EMPLOYEE]: state => state,
  [GET_ORG]: state => state,
  [GET_VALIDITY]: state => state
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

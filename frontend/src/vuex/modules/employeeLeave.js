import { LEAVE_EMPLOYEE, SET_EMPLOYEE, SET_VALIDITY, GET_EMPLOYEE, GET_VALIDITY } from '../actions/employeeLeave'
import Service from '@/api/HttpCommon'

const state = {
  employee: {},
  validity: {
    from: '',
    to: ''
  }
}

const actions = {
  [LEAVE_EMPLOYEE] ({commit, state}, payload) {
    return Service.createEntry(state.employee.uuid, state.validity)
      .then(response => {
        if (response.data.error) {
          return response.data
        }
        // store.commit('log/newWorkLog', {type: 'EMPLOYEE_LEAVE', value: response.data})
        return response.data
      })
  }
}

const mutations = {
  change (state, employee) {
    state.employee = employee.employee
    state.validity = employee.validity
  },
  [SET_EMPLOYEE] (state, payload) {
    state.employee = payload
  },
  [SET_VALIDITY] (state, payload) {
    state.validity = payload
  }
}

const getters = {
  getUuid: state => state.uuid,
  get: state => state,
  [GET_EMPLOYEE]: state => state.employee,
  [GET_VALIDITY]: state => state.validity
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

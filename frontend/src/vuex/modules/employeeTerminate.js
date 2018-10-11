import { TERMINATE_EMPLOYEE, SET_EMPLOYEE, SET_ENDDATE, GET_EMPLOYEE, GET_ENDDATE } from '../actions/employeeTerminate'
import Service from '@/api/HttpCommon'

const state = {
  employee: {},
  validity: {
    to: ''
  }
}

const actions = {
  [TERMINATE_EMPLOYEE] ({commit, state}, payload) {
    return Service.post(`/e/${state.employee.uuid}/terminate`, state.validity.to)
      .then(response => {
        // EventBus.$emit('employee-changed')
        // store.commit('log/newWorkLog', {type: 'EMPLOYEE_TERMINATE', value: response.data})
        return response.data
      })
      .catch(error => {
        // store.commit('log/newError', {type: 'ERROR', value: error.response})
        return error.response
      })
  }
}

const mutations = {
  change (state, employee) {
    state.employee = employee.employee
    state.validity.to = employee.validity.to
  },
  [SET_EMPLOYEE] (state, payload) {
    state.employee = payload
  },
  [SET_ENDDATE] (state, payload) {
    state.validity.to = payload
  }
}

const getters = {
  getUuid: state => state.uuid,
  get: state => state,
  [GET_EMPLOYEE]: state => state.employee,
  [GET_ENDDATE]: state => state.validity.to
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

import { LEAVE_EMPLOYEE, SET_EMPLOYEE, SET_LEAVE, GET_EMPLOYEE, GET_LEAVE } from '../actions/employeeLeave'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  employee: {},
  leave: {
    person: {},
    leave_type: {},
    type: 'leave',
    validity: {
      from: '',
      to: ''
    }
  }
}

const actions = {
  [LEAVE_EMPLOYEE] ({commit, state}, payload) {
    return Service.post('/details/create', [state.leave])
    .then(response => {
      if (response.data.error) {
        return response.data
      }
      EventBus.$emit('employee-changed')
      this.commit('log/newWorkLog', {type: 'EMPLOYEE_LEAVE', value: response.data})
      return response.data
    })
    .catch(error => {
      EventBus.$emit('employee-changed')
      this.commit('log/newError', {type: 'ERROR', value: error.response})
      return error.response
    })
  }
}

const mutations = {
  change (state, employee) {
    state.employee = employee.employee
    state.leave = employee.leave
  },
  [SET_EMPLOYEE] (state, payload) {
    state.employee = payload
  },
  [SET_LEAVE] (state, payload) {
    state.leave = payload
  }
}

const getters = {
  getUuid: state => state.uuid,
  get: state => state,
  [GET_EMPLOYEE]: state => state.employee,
  [GET_LEAVE]: state => state.leave
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

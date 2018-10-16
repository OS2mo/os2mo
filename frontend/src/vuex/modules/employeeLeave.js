import { LEAVE_EMPLOYEE, SET_EMPLOYEE, SET_LEAVE, GET_EMPLOYEE, GET_LEAVE } from '../actions/employeeLeave'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  person: {},
  leave_type: {},
  type: 'leave',
  validity: {
    from: '',
    to: ''
  }
}

const actions = {
  [LEAVE_EMPLOYEE] ({commit, state}, payload) {
    return Service.post('/details/create', [state])
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
      this.commit('log/newError', {type: 'ERROR', value: error.response.data})
      return error.response.data
    })
  }
}

const mutations = {
  change (state, employee) {
    state.person = employee.person
    state.leave_type = employee.leave_type
    state.validity = employee.validity
  },
  [SET_EMPLOYEE] (state, payload) {
    state.person = payload
  },
  [SET_LEAVE] (state, payload) {
    state = payload
  }
}

const getters = {
  getUuid: state => state.uuid,
  get: state => state,
  [GET_EMPLOYEE]: state => state.person,
  [GET_LEAVE]: state => state
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}

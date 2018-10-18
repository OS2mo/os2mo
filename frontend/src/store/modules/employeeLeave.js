import { getField, updateField } from 'vuex-map-fields'
import Service from '@/api/HttpCommon'
import { EventBus } from '@/EventBus'

const state = {
  employee: {},
  leave: {}
}

const actions = {
  LEAVE_EMPLOYEE ({ commit, state }) {
    let payload = state.leave
    payload.person = state.employee

    // todo: all create calls are shared now. refactor to one central handler
    return Service.post('/details/create', [payload])
      .then(response => {
        if (response.data.error) {
          return response.data
        }
        EventBus.$emit('employee-changed')
        commit('log/newWorkLog', { type: 'EMPLOYEE_LEAVE', value: response.data }, { root: true })
        return response.data
      })
      .catch(error => {
        EventBus.$emit('employee-changed')
        commit('log/newError', { type: 'ERROR', value: error.response.data }, { root: true })
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
    state.employee = {}
    state.leave = {}
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
